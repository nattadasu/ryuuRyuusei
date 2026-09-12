import os
import re
import shutil
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import aiohttp
import interactions as ipy

from classes.anilist import AniList
from classes.database import UserDatabase
from classes.excepts import ProviderHttpError
from modules.anilist_token import (
    REFRESH_THRESHOLD,
    clear_token,
    exchange_pin,
    get_authorize_url,
    load_token,
    save_token,
)
from modules.const import (
    AUTHOR_USERID,
    EMOJI_SUCCESS,
    EMOJI_UNEXPECTED_ERROR,
    EMOJI_USER_ERROR,
    VERIFICATION_SERVER,
    VERIFIED_ROLE,
)
from modules.crypto_utils import CryptoUtils
from modules.discord import format_username

ANILIST_PIN_MODAL = "hostsettings_anilist_pin"
"""Custom ID of the AniList PIN modal"""
ANILIST_PIN_INPUT = "anilist_pin"
"""Custom ID of the PIN text input inside the modal"""
ANILIST_PIN_BUTTON = "hostsettings_anilist_pin_button"
"""Custom ID of the button that opens the PIN modal"""

hostsettings_head = ipy.SlashCommand(
    name="hostsettings",
    description="Change the bot settings, for self-hosted bot only",
    scopes=[
        AUTHOR_USERID,
        VERIFICATION_SERVER,
    ],
    dm_permission=False,
)


class HostSettings(ipy.Extension):
    """Host Settings commands"""

    member = hostsettings_head.group(
        name="member", description="Manage member settings, for self-hosted bot only"
    )

    database = hostsettings_head.group(
        name="database",
        description="Manage database settings, for self-hosted bot only",
    )

    anilist = hostsettings_head.group(
        name="anilist",
        description="Manage AniList host authentication, for self-hosted bot only",
    )

    @member.subcommand(
        sub_cmd_name="verify",
        sub_cmd_description="Verify a user in the club",
        options=[
            ipy.SlashCommandOption(
                name="user",
                description="User to verify",
                required=True,
                type=ipy.OptionType.USER,
            )
        ],
    )
    async def hostsettings_member_verify(
        self, ctx: ipy.SlashContext, user: ipy.Member | ipy.User
    ):
        await ctx.defer(ephemeral=True)
        embed = ipy.Embed()
        if int(ctx.guild.id) != int(VERIFICATION_SERVER):
            embed = self.generate_error_embed(
                header="Error!",
                message=f"This command can only be used in the server that hosted this bot ({VERIFICATION_SERVER})!",
                is_user_error=False,
            )
            await ctx.send(embed=embed)
            return
        async with UserDatabase() as ud:
            is_registered = await ud.check_if_registered(user.id)
            if is_registered is False:
                embed = self.generate_error_embed(
                    header="Error!",
                    message="User is not registered!",
                    is_user_error=True,
                )
                await ctx.send(embed=embed)
                return
            status = await ud.verify_user(ctx.author.id)

        user_roles = [str(role.id) for role in ctx.author.roles]  # type: ignore

        # check if verified role exists
        if status is True and str(VERIFIED_ROLE) not in user_roles:
            await ctx.member.add_role(
                VERIFIED_ROLE,
                reason=f"User verified via slash command by {format_username(ctx.author)} ({ctx.author.id})",
            ) if ctx.member else None
            embed = self.generate_success_embed(
                header="Success!",
                message="User have been verified!",
            )
        elif status is True and str(VERIFIED_ROLE) in user_roles:
            embed = self.generate_error_embed(
                header="Error!",
                message="User is already verified!",
                is_user_error=True,
            )

        await ctx.send(embed=embed)

    @database.subcommand(
        sub_cmd_name="export",
        sub_cmd_description="Export and encrypt all databases and configuration",
    )
    async def hostsettings_database_export(self, ctx: ipy.SlashContext):
        await ctx.defer(ephemeral=True)

        with tempfile.TemporaryDirectory() as tmpdir:
            temp_dir_to_archive = Path(tmpdir) / "backup_content"
            temp_dir_to_archive.mkdir()

            # Add database directory
            if os.path.exists("database"):
                shutil.copytree(
                    "database", temp_dir_to_archive / "database", dirs_exist_ok=True
                )

            # Add .env file
            if os.path.exists(".env"):
                shutil.copy2(".env", temp_dir_to_archive / ".env")

            # Add any private_ files/folders (e.g., extensions/private_seasonal.py)
            for path in Path(".").rglob("private_*"):
                if (
                    "__pycache__" in str(path)
                    or ".mypy_cache" in str(path)
                    or ".ruff_cache" in str(path)
                ):
                    continue

                relative_path = path.relative_to(".")
                dest_path = temp_dir_to_archive / relative_path

                if path.is_dir():
                    shutil.copytree(path, dest_path, dirs_exist_ok=True)
                else:
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(path, dest_path)

            # Create tar archive
            archive_path_base = Path(tmpdir) / "backup"
            archive_path = Path(
                shutil.make_archive(
                    str(archive_path_base), "tar", root_dir=temp_dir_to_archive
                )
            )

            try:
                enc_path, key = CryptoUtils.encrypt_and_package(archive_path)
                file = ipy.File(str(enc_path), file_name="backup.tar.gz.enc")
                await ctx.send(
                    content=f"Backup exported successfully.\n**Encryption Key:** `{key}`\nKeep this key safe, you will need it to import the backup back.",
                    file=file,
                )
                enc_path.unlink()
            except Exception as e:  # noqa: BLE001
                embed = self.generate_error_embed(
                    header="Error!",
                    message=f"An error occurred during export: {e}",
                    is_user_error=False,
                )
                await ctx.send(embed=embed)

    @database.subcommand(
        sub_cmd_name="import",
        sub_cmd_description="Import and decrypt the backup (database and .env)",
        options=[
            ipy.SlashCommandOption(
                name="file",
                description="The encrypted backup file (.enc)",
                required=True,
                type=ipy.OptionType.ATTACHMENT,
            ),
            ipy.SlashCommandOption(
                name="key",
                description="The encryption key",
                required=True,
                type=ipy.OptionType.STRING,
            ),
        ],
    )
    async def hostsettings_database_import(
        self, ctx: ipy.SlashContext, file: ipy.Attachment, key: str
    ):
        await ctx.defer(ephemeral=True)
        temp_enc_path = Path("backup_temp.enc")
        temp_tar_path = Path("backup_temp.tar")

        try:
            # Download the file
            async with (
                aiohttp.ClientSession() as session,
                session.get(file.url) as resp,
            ):
                if resp.status == 200:
                    data = await resp.read()
                    temp_enc_path.write_bytes(data)
                else:
                    raise RuntimeError(
                        f"Failed to download attachment: HTTP {resp.status}"
                    )

            # Decrypt and decompress to tar
            CryptoUtils.decrypt_and_extract(temp_enc_path, key, temp_tar_path)

            # Create backup of current state
            if os.path.exists("database"):
                if os.path.exists("database_backup"):
                    shutil.rmtree("database_backup")
                shutil.copytree("database", "database_backup")
            if os.path.exists(".env"):
                shutil.copy2(".env", ".env.bak")

            # Extract tar
            with tarfile.open(temp_tar_path, "r") as tar:
                tar.extractall(path=".")

            # Delete temp files before restart
            if temp_enc_path.exists():
                temp_enc_path.unlink()
            if temp_tar_path.exists():
                temp_tar_path.unlink()

            embed = self.generate_success_embed(
                header="Success!",
                message="Backup imported and decrypted successfully! The bot will now restart.",
            )
            await ctx.send(embed=embed)

            # Trigger force_restart
            update_daemon = next(
                (
                    ext
                    for ext in self.bot.ext.values()
                    if ext.__class__.__name__ == "UpdateDaemon"
                ),
                None,
            )
            if update_daemon and hasattr(update_daemon, "force_restart"):
                await update_daemon.force_restart(ctx)
            else:
                # Fallback if extension not found
                pid = os.getpid()
                os.kill(pid, 9)

        except Exception as e:  # noqa: BLE001
            embed = self.generate_error_embed(
                header="Error!",
                message=f"An error occurred during import: {e}",
                is_user_error=False,
            )
            await ctx.send(embed=embed)
        finally:
            if temp_enc_path.exists():
                temp_enc_path.unlink()
            if temp_tar_path.exists():
                temp_tar_path.unlink()

    @anilist.subcommand(
        sub_cmd_name="status",
        sub_cmd_description="Show AniList host login status",
    )
    async def hostsettings_anilist_status(self, ctx: ipy.SlashContext):
        await ctx.defer(ephemeral=True)
        token = load_token()
        if token is None:
            embed = self.generate_error_embed(
                header="Not logged in",
                message="No AniList token stored. Use `/hostsettings anilist login` to authenticate.",
                is_user_error=True,
            )
            await ctx.send(embed=embed)
            return
        try:
            async with AniList() as anilist:
                viewer = await anilist.viewer()
        except ProviderHttpError as e:
            embed = self.generate_error_embed(
                header="Error!",
                message=f"Stored token was rejected by AniList: {e.message}\nUse `/hostsettings anilist login` to re-authenticate or `/hostsettings anilist logout` to clear it.",
                is_user_error=False,
            )
            await ctx.send(embed=embed)
            return
        adult = (viewer.get("options") or {}).get("displayAdultContent")
        if token.expires_at is None:
            expiry_value = "Unknown"
        else:
            stamp = int(token.expires_at)
            expiry_value = f"<t:{stamp}:F> (<t:{stamp}:R>)"
        threshold_days = REFRESH_THRESHOLD / 86400
        avatar = (viewer.get("avatar") or {}).get("large")
        embed = ipy.Embed(
            title="AniList Host Status",
            description=f"Logged in as [{viewer.get('name')}]({viewer.get('siteUrl')})",
            color=0x0AA4F5,
            timestamp=datetime.now(tz=timezone.utc),
        )
        if avatar:
            embed.set_thumbnail(url=avatar)
        embed.add_fields(
            ipy.EmbedField(name="User ID", value=str(viewer.get("id")), inline=True),
            ipy.EmbedField(
                name="Adult content",
                value="Enabled" if adult else "Disabled",
                inline=True,
            ),
            ipy.EmbedField(name="Token expires", value=expiry_value, inline=False),
            ipy.EmbedField(
                name="Auto-refresh",
                value=f"Enabled (checks every 12 hours, refreshes below {threshold_days:.0f} days left)",
                inline=False,
            ),
        )
        await ctx.send(embed=embed)

    @anilist.subcommand(
        sub_cmd_name="login",
        sub_cmd_description="Log in to AniList via PIN code",
    )
    async def hostsettings_anilist_login(self, ctx: ipy.SlashContext):
        url = get_authorize_url()
        embed = ipy.Embed(
            title="AniList Login",
            description=(
                "1. Open the link below and authorize the bot\n"
                f"{url}\n"
                "2. Copy the PIN shown by AniList\n"
                "3. Press **Enter PIN** and paste it"
            ),
            color=0x0AA4F5,
        )
        components = [
            ipy.Button(
                style=ipy.ButtonStyle.BLURPLE,
                label="Enter PIN",
                custom_id=ANILIST_PIN_BUTTON,
            )
        ]
        await ctx.send(embed=embed, components=components, ephemeral=True)

    @ipy.component_callback(ANILIST_PIN_BUTTON)
    async def anilist_pin_button(self, ctx: ipy.ComponentContext):
        """Open the modal to paste the AniList PIN"""
        modal = ipy.Modal(
            ipy.ShortText(
                label="AniList PIN",
                custom_id=ANILIST_PIN_INPUT,
                placeholder="Paste the PIN from the AniList page",
                required=True,
                min_length=1,
                max_length=1000,
            ),
            title="AniList Login",
            custom_id=ANILIST_PIN_MODAL,
        )
        await ctx.send_modal(modal=modal)

    @ipy.modal_callback(ANILIST_PIN_MODAL)
    async def anilist_pin_modal(self, ctx: ipy.ModalContext):
        """Exchange the pasted PIN for tokens and store them"""
        pin = (ctx.responses.get(ANILIST_PIN_INPUT) or "").strip()
        await ctx.defer(ephemeral=True)
        if not pin:
            embed = self.generate_error_embed(
                header="Error!",
                message="Empty PIN. Press **Enter PIN** and paste the code from AniList.",
                is_user_error=True,
            )
            await ctx.send(embed=embed)
            return
        try:
            token = await exchange_pin(pin)
        except ProviderHttpError as e:
            embed = self.generate_error_embed(
                header="Login failed!",
                message=f"AniList rejected the PIN: {e.message}",
                is_user_error=True,
            )
            await ctx.send(embed=embed)
            return
        save_token(token)
        try:
            async with AniList() as anilist:
                viewer = await anilist.viewer()
            account = f"[{viewer.get('name')}]({viewer.get('siteUrl')})"
        except ProviderHttpError:
            account = "your account"
        embed = self.generate_success_embed(
            header="Logged in!",
            message=f"Authenticated as {account}. Token stored securely and will refresh automatically.",
        )
        await ctx.send(embed=embed)

    @anilist.subcommand(
        sub_cmd_name="logout",
        sub_cmd_description="Log out of AniList (delete stored token)",
    )
    async def hostsettings_anilist_logout(self, ctx: ipy.SlashContext):
        await ctx.defer(ephemeral=True)
        if clear_token():
            embed = self.generate_success_embed(
                header="Logged out!",
                message="AniList token deleted. The bot now runs anonymously.",
            )
        else:
            embed = self.generate_error_embed(
                header="Error!",
                message="Not logged in, nothing to clear.",
                is_user_error=True,
            )
        await ctx.send(embed=embed)

    @staticmethod
    def generate_error_embed(
        header: str, message: str, is_user_error: bool = True
    ) -> ipy.Embed:
        """
        Generate an error embed

        Args:
            header (str): Header of the embed
            message (str): Message of the embed
            is_user_error (bool, optional): Whether the error is user's fault. Defaults to True.

        Returns:
            ipy.Embed: Error embed
        """
        emoji_id: int | None = None
        # grab emoji ID
        if is_user_error is True:
            emoji = re.search(r"<:(\w+):(\d+)>", EMOJI_USER_ERROR)
            if emoji is not None:
                emoji_id = int(emoji.group(2))
        else:
            emoji = re.search(r"<:(\w+):(\d+)>", EMOJI_UNEXPECTED_ERROR)
            if emoji is not None:
                emoji_id = int(emoji.group(2))
        embed = ipy.Embed(
            title=header,
            description=message,
            color=0xFF0000,
        )
        if emoji_id is not None:
            embed.set_thumbnail(
                url=f"https://cdn.discordapp.com/emojis/{emoji_id}.png?v=1"
            )
        return embed

    @staticmethod
    def generate_success_embed(header: str, message: str) -> ipy.Embed:
        """
        Generate a success embed

        Args:
            header (str): Header of the embed
            message (str): Message of the embed

        Returns:
            ipy.Embed: Success embed
        """
        emoji_id: int | None = None
        # grab emoji ID
        emoji = re.search(r"<:(\w+):(\d+)>", EMOJI_SUCCESS)
        if emoji is not None:
            emoji_id = int(emoji.group(2))
        embed = ipy.Embed(
            title=header,
            description=message,
            color=0x00FF00,
        )
        if emoji_id is not None:
            embed.set_thumbnail(
                url=f"https://cdn.discordapp.com/emojis/{emoji_id}.png?v=1"
            )
        return embed


def setup(bot: ipy.Client):
    HostSettings(bot)
