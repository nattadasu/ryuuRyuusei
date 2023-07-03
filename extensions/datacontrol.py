"""
Data Control Extension
======================

This extension is responsible for handling user data, such as registering,
updating, and deleting user data.
"""

import json
import os
import re
from datetime import datetime, timezone
from typing import Literal

import interactions as ipy
import pandas as pd
import yaml

from classes.anilist import AniList
from classes.cache import Caching
from classes.database import UserDatabase, UserDatabaseClass
from classes.excepts import ProviderHttpError
from classes.html.myanimelist import HtmlMyAnimeList
from classes.lastfm import LastFM
from classes.shikimori import Shikimori
from classes.verificator import Verificator
from modules.commons import save_traceback_to_file
from modules.const import (DECLINED_GDPR, EMOJI_SUCCESS,
                           EMOJI_UNEXPECTED_ERROR, EMOJI_USER_ERROR,
                           VERIFICATION_SERVER, VERIFIED_ROLE)


class DataControl(ipy.Extension):
    """Extension class for everything related to user data"""

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
                url=f"https://cdn.discordapp.com/emojis/{emoji_id}.png?v=1")
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
                url=f"https://cdn.discordapp.com/emojis/{emoji_id}.png?v=1")
        return embed

    async def _check_if_registered(
        self, ctx: ipy.ComponentContext | ipy.SlashContext
    ) -> bool:
        """
        Check if the user is registered

        Args:
            ctx (ipy.ComponentContext | ipy.SlashContext): Context

        Returns:
            bool: Whether the user is registered
        """
        async with UserDatabase() as udb:
            is_registered = await udb.check_if_registered(ctx.author.id)
            if is_registered is True:
                embed = self.generate_error_embed(
                    header="Look out!",
                    message="You are already registered!",
                    is_user_error=True,
                )
                await ctx.send(embed=embed)
                return True
            return False

    @ipy.cooldown(ipy.Buckets.USER, 1, 60)
    @ipy.slash_command(
        name="register",
        description="Register yourself to the database",
        options=[
            ipy.SlashCommandOption(
                name="mal_username",
                description="Your MyAnimeList username",
                type=ipy.OptionType.STRING,
                required=True,
            ),
            ipy.SlashCommandOption(
                name="accept_privacy_policy",
                description="Accept the privacy policy",
                type=ipy.OptionType.BOOLEAN,
                required=True,
            ),
        ],
    )
    async def register(
        self, ctx: ipy.SlashContext, mal_username: str, accept_privacy_policy: bool
    ):
        """
        Register yourself to the database

        Args:
            ctx (ipy.SlashContext): Context
            mal_username (str): MyAnimeList username
            accept_privacy_policy (bool): Whether the user accepts the privacy policy.
                This is required to register, or else the registration will be declined.
        """
        await ctx.defer(ephemeral=True)
        if accept_privacy_policy is False:
            await ctx.send(DECLINED_GDPR)
            return
        checker = await self._check_if_registered(ctx)
        if checker is True:
            return
        fields = [
            ipy.EmbedField(
                name="1. Sign in to MyAnimeList",
                value="To make thing easier, sign your account in on your default browser. [Click here to sign in](https://myanimelist.net/login.php).",
            ),
            ipy.EmbedField(
                name="2. Go to your profile settings",
                value="Once you are signed in, go to your profile settings. [Click here to go to your profile settings](https://myanimelist.net/editprofile.php).",
            ),
            ipy.EmbedField(
                name='3. Scroll down to "My Details" and find "Location"',
                value="Don't worry, you can change it back later.",
            ),
        ]

        overwrite_prompt = (
            "4. Copy the following text and overwrite/paste it into the Location field"
        )

        with Verificator() as verify:
            # check if user still have pending verification
            verification = verify.get_user_uuid(ctx.author.id)
            if verification is not None:
                remaining_time = verification.epoch_time + 43200
            else:
                verification = verify.save_user_uuid(
                    ctx.author.id, mal_username)
                remaining_time = verification.epoch_time + 43200
            fields.append(
                ipy.EmbedField(
                    name=overwrite_prompt,
                    value=f"```\n{verification.uuid}\n```**Note:** Verification code expires <t:{remaining_time}:R>.",
                ))
            epoch = ipy.Timestamp.fromtimestamp(
                verification.epoch_time, tz=timezone.utc)

        fields += [
            ipy.EmbedField(
                name="5. Save your changes",
                value="Once you are done, save your changes, then confirm your registration by clicking the button below.",
            ),
        ]
        embed = ipy.Embed(
            title="Registration",
            description=f"""## Hi, {ctx.author.display_name}!

To complete your registration, please follow the instructions below:""",
            footer=ipy.EmbedFooter(
                text="If you have any questions, feel free to contact the developer. Verification codes are valid for 12 hours.",
            ),
            timestamp=epoch,
            color=0x7289DA,
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        embed.add_fields(*fields)
        components = [
            ipy.Button(
                style=ipy.ButtonStyle.BLURPLE,
                label="Confirm registration",
                custom_id="account_register",
            )
        ]
        await ctx.send(embed=embed, components=components)

    @ipy.component_callback("account_register")
    async def callback_registration(self, ctx: ipy.ComponentContext):
        """Check and confirm user registration"""
        await ctx.defer(ephemeral=True)
        checker = await self._check_if_registered(ctx)
        if checker is True:
            return
        # check if user location matches the generated uuid
        with Verificator() as verify:
            user_code = verify.get_user_uuid(ctx.author.id)
        if user_code is not None:
            mal_username = user_code.mal_username
        else:
            return
        async with HtmlMyAnimeList() as hmal:
            mal_data = await hmal.get_user(mal_username)
            mal_id = mal_data.mal_id
            mal_joined = mal_data.joined
            user_location = mal_data.location
        if user_location != user_code.uuid:
            embed = self.generate_error_embed(
                header="Look out!",
                message="Your location does not match the generated code. Please try again.",
                is_user_error=True,
            )
            await ctx.send(embed=embed)
            return

        guild = ctx.guild
        if guild is None:
            guild_name = "Personal DM"
            guild_id = ctx.author.id
        else:
            guild_name = guild.name
            guild_id = guild.id

        async with UserDatabase() as udb:
            await udb.save_to_database(
                UserDatabaseClass(
                    discord_id=ctx.author.id,
                    discord_username=ctx.author.username,
                    mal_id=mal_id,
                    mal_username=mal_username,
                    mal_joined=mal_joined,
                    registered_at=datetime.now(tz=timezone.utc),
                    registered_guild_id=guild_id,
                    registered_guild_name=guild_name,
                    registered_by=ctx.author.id,
                )
            )
        embed = self.generate_success_embed(
            header="Success!",
            message="You have been registered!",
        )
        cache_ = Caching("cache/verify", 43200)
        path = f"{ctx.author.id}.json"
        file_path = cache_.get_cache_path(path)
        await ctx.send(embed=embed)
        cache_.drop_cache(file_path)
        return

    @ipy.cooldown(ipy.Buckets.USER, 1, 5)
    @ipy.slash_command(
        name="platform",
        description="Platform linking utility",
        sub_cmd_name="link",
        sub_cmd_description="Link a platform",
        options=[
            ipy.SlashCommandOption(
                name="platform",
                description="Platform to link",
                type=ipy.OptionType.STRING,
                required=True,
                choices=[
                    ipy.SlashCommandChoice(
                        name="AniList",
                        value="anilist",
                    ),
                    ipy.SlashCommandChoice(
                        name="Last.fm",
                        value="lastfm",
                    ),
                    ipy.SlashCommandChoice(
                        name="Shikimori",
                        value="shikimori",
                    ),
                ],
            ),
            ipy.SlashCommandOption(
                name="username",
                description="Your username on the platform",
                type=ipy.OptionType.STRING,
                required=True,
            ),
        ],
    )
    async def platform_link(
        self,
        ctx: ipy.SlashContext,
        platform: Literal["anilist", "lastfm", "shikimori"],
        username: str,
    ):
        """
        Link your account to a platform

        Platforms:
            - AniList
            - Last.fm
            - Shikimori

        Args:
            platform (Literal["anilist", "lastfm", "shikimori"]): Platform to link
            username (str): Your username on the platform
        """
        await ctx.defer(ephemeral=True)
        async with UserDatabase() as udb:
            is_registered = await udb.check_if_registered(ctx.author.id)
            if is_registered is False:
                await ctx.send("You are not registered!")
                return
        try:
            if platform == "anilist":
                async with AniList() as anilist:
                    user_data = await anilist.user(username, return_id=True)
                    user_id = user_data.id
                async with UserDatabase() as udb:
                    await udb.update_user(
                        ctx.author.id, row="anilistId", modified_input=user_id
                    )
                    await udb.update_user(
                        ctx.author.id, row="anilistUsername", modified_input=username
                    )
            elif platform == "lastfm":
                async with LastFM() as lastfm:
                    await lastfm.get_user_info(username)
                async with UserDatabase() as udb:
                    await udb.update_user(
                        ctx.author.id, row="lastfmUsername", modified_input=username
                    )
            elif platform == "shikimori":
                async with Shikimori() as shikimori:
                    user_data = await shikimori.get_user(username)
                    user_id = user_data.id
                async with UserDatabase() as udb:
                    await udb.update_user(
                        ctx.author.id, row="shikimoriId", modified_input=user_id
                    )
                    await udb.update_user(
                        ctx.author.id, row="shikimoriUsername", modified_input=username
                    )
            embed = self.generate_success_embed(
                header="Success!",
                message=f"Your {platform} account has been linked!",
            )
            await ctx.send(embed=embed)
        except ProviderHttpError as error:
            embed = self.generate_error_embed(
                header="Error!",
                message=(
                    "User can't be found"
                    if error.status_code == 404
                    else "Unable to fetch information from platform's server"
                ),
                is_user_error=False,
            )
            await ctx.send(embed=embed)
            save_traceback_to_file("platform_link", ctx.author, error)
        # pylint: disable-next=broad-except
        except Exception as error:
            embed = self.generate_error_embed(
                header="Error!",
                message=f"Something went wrong: {error}",
                is_user_error=False,
            )
            await ctx.send(embed=embed)
            save_traceback_to_file("platform_link", ctx.author, error)

    @ipy.cooldown(ipy.Buckets.USER, 1, 5)
    @ipy.slash_command(
        name="platform",
        description="Platform linking utility",
        sub_cmd_name="unlink",
        sub_cmd_description="Unlink a platform",
        options=[
            ipy.SlashCommandOption(
                name="platform",
                description="Platform to unlink",
                type=ipy.OptionType.STRING,
                required=True,
                choices=[
                    ipy.SlashCommandChoice(
                        name="AniList",
                        value="anilist",
                    ),
                    ipy.SlashCommandChoice(
                        name="Last.fm",
                        value="lastfm",
                    ),
                    ipy.SlashCommandChoice(
                        name="Shikimori",
                        value="shikimori",
                    ),
                ],
            ),
        ],
    )
    async def platform_unlink(
        self, ctx: ipy.SlashContext, platform: Literal["anilist", "lastfm", "shikimori"]
    ):
        """
        Unink your account from a platform

        Platforms:
            - AniList
            - Last.fm
            - Shikimori

        Args:
            platform (Literal["anilist", "lastfm", "shikimori"]): Platform to unlink
        """
        await ctx.defer(ephemeral=True)
        async with UserDatabase() as udb:
            is_registered = await udb.check_if_registered(ctx.author.id)
            if is_registered is False:
                await ctx.send("You are not registered!")
                return
        try:
            if platform == "anilist":
                async with UserDatabase() as udb:
                    await udb.update_user(
                        ctx.author.id, row="anilistId", modified_input=None
                    )
                    await udb.update_user(
                        ctx.author.id, row="anilistUsername", modified_input=None
                    )
            elif platform == "lastfm":
                async with UserDatabase() as udb:
                    await udb.update_user(
                        ctx.author.id, row="lastfmUsername", modified_input=None
                    )
            elif platform == "shikimori":
                async with UserDatabase() as udb:
                    await udb.update_user(
                        ctx.author.id, row="shikimoriId", modified_input=None
                    )
                    await udb.update_user(
                        ctx.author.id, row="shikimoriUsername", modified_input=None
                    )
            embed = self.generate_success_embed(
                header="Success!",
                message=f"Your {platform} account has been unlinked!",
            )
            await ctx.send(embed=embed)
        except ProviderHttpError as error:
            embed = self.generate_error_embed(
                header="Error!",
                message=error.message,
                is_user_error=False,
            )
            await ctx.send(embed=embed)
            save_traceback_to_file("platform_unlink", ctx.author, error)

    @ipy.cooldown(ipy.Buckets.USER, 1, 60)
    @ipy.slash_command(
        name="unregister",
        description="Unregister from the bot",
    )
    async def unregister(self, ctx: ipy.SlashContext):
        """Unregister from the bot"""
        await ctx.defer(ephemeral=True)
        async with UserDatabase() as udb:
            is_registered = await udb.check_if_registered(ctx.author.id)
            if is_registered is False:
                embed = self.generate_error_embed(
                    header="Error!",
                    message="You are not registered!",
                    is_user_error=True,
                )
                await ctx.send(embed=embed)
                return
            await udb.drop_user(ctx.author.id)
        embed = self.generate_success_embed(
            header="Success!",
            message="You have been unregistered!",
        )
        await ctx.send(embed=embed)

    @ipy.cooldown(ipy.Buckets.USER, 1, 3600)
    @ipy.slash_command(
        name="export",
        description="Export data utility",
        sub_cmd_name="data",
        sub_cmd_description="Export your data",
        options=[
            ipy.SlashCommandOption(
                name="file_format",
                description="File format to export to",
                type=ipy.OptionType.STRING,
                required=False,
                choices=[
                    ipy.SlashCommandChoice(
                        name="JSON (Default)",
                        value="json",
                    ),
                    ipy.SlashCommandChoice(
                        name="CSV",
                        value="csv",
                    ),
                    ipy.SlashCommandChoice(
                        name="YAML",
                        value="yaml",
                    ),
                    ipy.SlashCommandChoice(
                        name="Python Dict",
                        value="py",
                    ),
                ],
            ),
        ],
    )
    async def export_data(
        self,
        ctx: ipy.SlashContext,
        file_format: Literal["json", "csv", "yaml", "py"] = "json",
    ):
        """
        Exports user data to preferred format

        Args:
            file_format (Literal["json", "csv", "yaml", "py"], optional): File format to export to. Defaults to "json".
        """
        await ctx.defer(ephemeral=True)
        async with UserDatabase() as udb:
            is_registered = await udb.check_if_registered(ctx.author.id)
            if is_registered is False:
                embed = self.generate_error_embed(
                    header="Error!",
                    message="You are not registered!",
                    is_user_error=True,
                )
                await ctx.send(embed=embed)
                return
            user_data = await udb.export_user_data(ctx.author.id)
            user_data = json.loads(user_data)

        filename = f"cache/export_{ctx.author.id}_{int(datetime.now(tz=timezone.utc).timestamp())}"

        match file_format:
            case "json":
                with open(f"{filename}.json", "w", encoding="utf-8") as file:
                    json.dump(user_data, file, indent=4)
            case "csv":
                dataframe = pd.DataFrame([user_data])
                dataframe.to_csv(
                    f"{filename}.csv",
                    index=False,
                    sep="\t",
                    encoding="utf-8",
                    header=True)
            case "py":
                with open(f"{filename}.py", "w", encoding="utf-8") as file:
                    file.write(f"""from typing import Union, TypedDict

class UserData(TypedDict):
    \"\"\"User data\"\"\"

    discordId: int
    \"\"\"Discord ID\"\"\"
    discordUsername: Union[str, None]
    \"\"\"Discord username\"\"\"
    discordJoined: int
    \"\"\"Discord joined timestamp\"\"\"
    malUsername: Union[str, None]
    \"\"\"MyAnimeList username\"\"\"
    malId: int
    \"\"\"MyAnimeList ID\"\"\"
    malJoined: int
    \"\"\"MyAnimeList joined timestamp\"\"\"
    registeredAt: int
    \"\"\"Registered timestamp\"\"\"
    registeredGuildId: int
    \"\"\"Registered guild ID\"\"\"
    registeredBy: int
    \"\"\"Registered by\"\"\"
    registeredGuildName: Union[str, None]
    \"\"\"Registered guild name\"\"\"
    anilistUsername: Union[str, None]
    \"\"\"AniList username\"\"\"
    anilistId: Union[int, None]
    \"\"\"AniList ID\"\"\"
    lastfmUsername: Union[str, None]
    \"\"\"Last.fm username\"\"\"
    shikimoriId: Union[int, None]
    \"\"\"Shikimori ID\"\"\"
    shikimoriUsername: Union[str, None]
    \"\"\"Shikimori username\"\"\"
    settings_language: str
    \"\"\"Language setting\"\"\"

user_data: UserData = {user_data}""")
            case "yaml":
                with open(f"{filename}.yaml", "w", encoding="utf-8") as file:
                    yaml.dump(user_data, file, indent=4)

        filename_formatted = f"{filename}.{file_format}"

        embed = self.generate_success_embed(
            header="Success!",
            message=f"Your data has been exported to `{filename_formatted.replace('cache/','')}`!\nFeel free to download the file!",
        )

        await ctx.send(
            embed=embed, file=ipy.File(
                f"{filename_formatted}", file_name=f"{filename_formatted}".replace("cache/", ""))
        )

        # Delete the file
        os.remove(f"{filename_formatted}")

    @ipy.cooldown(ipy.Buckets.USER, 1, 10)
    @ipy.slash_command(
        name="verify",
        description="Verify your account",
        dm_permission=False,
        scopes=[VERIFICATION_SERVER],
    )
    async def verify(self, ctx: ipy.SlashContext):
        """Verify your account"""
        await ctx.defer(ephemeral=True)
        async with UserDatabase() as udb:
            is_registered = await udb.check_if_registered(ctx.author.id)
            if is_registered is False:
                embed = self.generate_error_embed(
                    header="Error!",
                    message="You are not registered!",
                    is_user_error=True,
                )
                await ctx.send(embed=embed)
                return
            status = await udb.verify_user(ctx.author.id)

        if isinstance(ctx.author, ipy.Member):
            user_roles = [str(role.id) for role in ctx.author.roles]
        else:
            user_roles = []

        embed = self.generate_error_embed(
            header="Error!",
            message="Unknown error!",
            is_user_error=True,
        )

        # check if verified role exists
        if status is True and str(VERIFIED_ROLE) not in user_roles and isinstance(ctx.member, ipy.Member):
            await ctx.member.add_role(
                VERIFIED_ROLE, reason="User verified via slash command"
            )
            embed = self.generate_success_embed(
                header="Success!",
                message="You have been verified!",
            )
        elif status is True and str(VERIFIED_ROLE) in user_roles:
            embed = self.generate_error_embed(
                header="Error!",
                message="You are already verified!",
                is_user_error=True,
            )

        await ctx.send(embed=embed)


def setup(bot: ipy.AutoShardedClient):
    """Load the DataControl cog."""
    DataControl(bot)
