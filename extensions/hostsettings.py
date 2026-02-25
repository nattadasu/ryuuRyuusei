import os
import re
import shutil
import tarfile
import tempfile
from pathlib import Path

import aiohttp
import interactions as ipy

from classes.database import UserDatabase
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
            except Exception as e:
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
            async with aiohttp.ClientSession() as session:
                async with session.get(file.url) as resp:
                    if resp.status == 200:
                        data = await resp.read()
                        temp_enc_path.write_bytes(data)
                    else:
                        raise Exception(
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

        except Exception as e:
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
