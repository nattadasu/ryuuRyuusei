import json
import os
import re
from datetime import datetime, timezone
from typing import Literal

import interactions as ipy
import pandas as pd
import yaml

from classes.anilist import AniList
from classes.database import UserDatabase, UserDatabaseClass
from classes.excepts import ProviderHttpError
from classes.jikan import JikanApi
from classes.lastfm import LastFM
from classes.shikimori import Shikimori
from modules.const import (
    DECLINED_GDPR,
    EMOJI_SUCCESS,
    EMOJI_UNEXPECTED_ERROR,
    EMOJI_USER_ERROR,
    VERIFICATION_SERVER,
    VERIFIED_ROLE,
)


class DataControl(ipy.Extension):
    """Extension class for everything related to user data"""

    def __init__(self, bot: ipy.AutoShardedClient):
        self.bot = bot

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
        # grab emoji ID
        if is_user_error is True:
            emoji = re.search(r"<:(\w+):(\d+)>", EMOJI_USER_ERROR)
            emoji_id = int(emoji.group(2))
        else:
            emoji = re.search(r"<:(\w+):(\d+)>", EMOJI_UNEXPECTED_ERROR)
            emoji_id = int(emoji.group(2))
        embed = ipy.Embed(
            title=header,
            description=message,
            color=0xFF0000,
        )
        embed.set_thumbnail(url=f"https://cdn.discordapp.com/emojis/{emoji_id}.png?v=1")
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
        # grab emoji ID
        emoji = re.search(r"<:(\w+):(\d+)>", EMOJI_SUCCESS)
        emoji_id = int(emoji.group(2))
        embed = ipy.Embed(
            title=header,
            description=message,
            color=0x00FF00,
        )
        embed.set_thumbnail(url=f"https://cdn.discordapp.com/emojis/{emoji_id}.png?v=1")
        return embed

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
        await ctx.defer(ephemeral=True)
        if accept_privacy_policy is False:
            await ctx.send(DECLINED_GDPR)
            return
        async with UserDatabase() as ud:
            is_registered = await ud.check_if_registered(ctx.author.id)
            if is_registered is True:
                embed = self.generate_error_embed(
                    header="Look out!",
                    message="You are already registered!",
                    is_user_error=True,
                )
                await ctx.send(embed=embed)
                return
        async with JikanApi() as jikan:
            mal = await jikan.get_user_data(mal_username)
            mal_id = mal.mal_id
            mal_joined = mal.joined

        async with UserDatabase() as ud:
            await ud.save_to_database(
                UserDatabaseClass(
                    discord_id=ctx.author.id,
                    discord_username=ctx.author.username,
                    mal_id=mal_id,
                    mal_username=mal_username,
                    mal_joined=mal_joined,
                    registered_at=datetime.now(tz=timezone.utc),
                    registered_guild_id=ctx.guild.id,
                    registered_guild_name=ctx.guild.name,
                    registered_by=ctx.author.id,
                )
            )
        embed = self.generate_success_embed(
            header="Success!",
            message="You have been registered!",
        )
        await ctx.send(embed=embed)

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
        await ctx.defer(ephemeral=True)
        async with UserDatabase() as ud:
            is_registered = await ud.check_if_registered(ctx.author.id)
            if is_registered is False:
                await ctx.send("You are not registered!")
                return
        try:
            if platform == "anilist":
                async with AniList() as anilist:
                    user_id = await anilist.user(username)
                    user_id = user_id["id"]
                async with UserDatabase() as ud:
                    await ud.update_user(
                        ctx.author.id, row="anilistId", modified_input=user_id
                    )
                    await ud.update_user(
                        ctx.author.id, row="anilistUsername", modified_input=username
                    )
            elif platform == "lastfm":
                async with LastFM() as lastfm:
                    await lastfm.get_user_info(username)
                async with UserDatabase() as ud:
                    await ud.update_user(
                        ctx.author.id, row="lastfmUsername", modified_input=username
                    )
            elif platform == "shikimori":
                async with Shikimori() as shikimori:
                    user_id = await shikimori.get_user(username)
                    user_id = user_id.id
                async with UserDatabase() as ud:
                    await ud.update_user(
                        ctx.author.id, row="shikimoriId", modified_input=user_id
                    )
                    await ud.update_user(
                        ctx.author.id, row="shikimoriUsername", modified_input=username
                    )
            embed = self.generate_success_embed(
                header="Success!",
                message=f"Your {platform} account has been linked!",
            )
            await ctx.send(embed=embed)
        except ProviderHttpError as e:
            embed = self.generate_error_embed(
                header="Error!",
                message=e.message,
                is_user_error=False,
            )
            await ctx.send(embed=embed)

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
        await ctx.defer(ephemeral=True)
        async with UserDatabase() as ud:
            is_registered = await ud.check_if_registered(ctx.author.id)
            if is_registered is False:
                await ctx.send("You are not registered!")
                return
        try:
            if platform == "anilist":
                async with UserDatabase() as ud:
                    await ud.update_user(
                        ctx.author.id, row="anilistId", modified_input=None
                    )
                    await ud.update_user(
                        ctx.author.id, row="anilistUsername", modified_input=None
                    )
            elif platform == "lastfm":
                async with UserDatabase() as ud:
                    await ud.update_user(
                        ctx.author.id, row="lastfmUsername", modified_input=None
                    )
            elif platform == "shikimori":
                async with UserDatabase() as ud:
                    await ud.update_user(
                        ctx.author.id, row="shikimoriId", modified_input=None
                    )
                    await ud.update_user(
                        ctx.author.id, row="shikimoriUsername", modified_input=None
                    )
            embed = self.generate_success_embed(
                header="Success!",
                message=f"Your {platform} account has been unlinked!",
            )
            await ctx.send(embed=embed)
        except ProviderHttpError as e:
            embed = self.generate_error_embed(
                header="Error!",
                message=e.message,
                is_user_error=False,
            )
            await ctx.send(embed=embed)

    @ipy.slash_command(
        name="unregister",
        description="Unregister from the bot",
    )
    async def unregister(self, ctx: ipy.SlashContext):
        await ctx.defer(ephemeral=True)
        async with UserDatabase() as ud:
            is_registered = await ud.check_if_registered(ctx.author.id)
            if is_registered is False:
                embed = self.generate_error_embed(
                    header="Error!",
                    message="You are not registered!",
                    is_user_error=True,
                )
                await ctx.send(embed=embed)
                return
            await ud.drop_user(ctx.author.id)
        embed = self.generate_success_embed(
            header="Success!",
            message="You have been unregistered!",
        )
        await ctx.send(embed=embed)

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
                required=True,
                choices=[
                    ipy.SlashCommandChoice(
                        name="JSON",
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
        self, ctx: ipy.SlashContext, file_format: Literal["json", "csv", "yaml"]
    ):
        await ctx.defer(ephemeral=True)
        async with UserDatabase() as ud:
            is_registered = await ud.check_if_registered(ctx.author.id)
            if is_registered is False:
                embed = self.generate_error_embed(
                    header="Error!",
                    message="You are not registered!",
                    is_user_error=True,
                )
                await ctx.send(embed=embed)
                return
            user_data = await ud.export_user_data(ctx.author.id)
            user_data = json.loads(user_data)

        filename = f"cache/export_{ctx.author.id}_{int(datetime.now(tz=timezone.utc).timestamp())}"

        # stringify json
        jd = json.dumps(user_data)
        if file_format == "json":
            with open(f"{filename}.json", "w") as f:
                json.dump(user_data, f, indent=4)
        elif file_format == "csv":
            df = pd.DataFrame([user_data])
            df.to_csv(
                f"{filename}.csv", index=False, sep="\t", encoding="utf-8", header=True
            )
        elif file_format == "yaml":
            with open(f"{filename}.yaml", "w") as f:
                yaml.dump(user_data, f, indent=4)
        elif file_format == "py":
            with open(f"{filename}.py", "w") as f:
                f.write(
                    f"""from typing import Union, TypedDict

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

user_data: UserData = {user_data}
"""
                )

        fn = f"{filename}.{file_format}"

        embed = self.generate_success_embed(
            header="Success!",
            message=f"Your data has been exported to `{fn.replace('cache/','')}`!\nFeel free to download the file!\n\nYour data in JSON format:\n```json\n{jd}```",
        )

        await ctx.send(
            embed=embed, file=ipy.File(f"{fn}", file_name=f"{fn}".replace("cache/", ""))
        )

        # Delete the file
        os.remove(f"{fn}")

    @ipy.slash_command(
        name="verify",
        description="Verify your account",
        dm_permission=False,
        scopes=[VERIFICATION_SERVER],
    )
    async def verify(self, ctx: ipy.SlashContext):
        await ctx.defer(ephemeral=True)
        async with UserDatabase() as ud:
            is_registered = await ud.check_if_registered(ctx.author.id)
            if is_registered is False:
                embed = self.generate_error_embed(
                    header="Error!",
                    message="You are not registered!",
                    is_user_error=True,
                )
                await ctx.send(embed=embed)
                return
            status = await ud.verify_user(ctx.author.id)

        user_roles = [str(role.id) for role in ctx.author.roles]

        # check if verified role exists
        if status is True and str(VERIFIED_ROLE) not in user_roles:
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
    DataControl(bot)
