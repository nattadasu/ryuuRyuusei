import re
from datetime import datetime, timezone
from typing import Literal

import interactions as ipy

from classes.cache import Caching
from classes.database import UserDatabase, UserDatabaseClass
from classes.html.myanimelist import HtmlMyAnimeList
from classes.verificator import Verificator
from modules.const import (EMOJI_FORBIDDEN, EMOJI_SUCCESS,
                           EMOJI_UNEXPECTED_ERROR, EMOJI_USER_ERROR)


class ServerSettings(ipy.Extension):
    """Server Settings commands"""

    serversettings_head = ipy.SlashCommand(
        name="serversettings",
        description="Change the bot settings server-wide",
        default_member_permissions=ipy.Permissions.MANAGE_GUILD | ipy.Permissions.ADMINISTRATOR,
        dm_permission=False,
    )

    member = serversettings_head.group(
        name="member",
        description="Manage member settings on this server",
    )

    async def _check_if_registered(
        self,
        ctx: ipy.ComponentContext | ipy.SlashContext,
        user: ipy.Member | ipy.User,
    ) -> bool:
        """
        Check if the user is registered

        Args:
            ctx (ipy.ComponentContext | ipy.SlashContext): Context
            user (ipy.Member | ipy.User): User to check

        Returns:
            bool: Whether the user is registered
        """
        async with UserDatabase() as udb:
            is_registered = await udb.check_if_registered(user.id)
            if is_registered is True:
                embed = self.generate_error_embed(
                    header="Look out!",
                    message="User is already registered!",
                    is_user_error=True,
                )
                await ctx.send(embed=embed)
                return True
            return False

    async def _check_if_platform_registered(
        self,
        ctx: ipy.ComponentContext | ipy.SlashContext,
        platform: Literal['mal', 'anilist', 'lastfm', 'shikimori'],
        value: str,
    ) -> bool:
        """
        Check if the user has registered a platform

        Args:
            ctx (ipy.ComponentContext | ipy.SlashContext): Context
            platform (str): Platform to check
            value (str): Value to check

        Returns:
            bool: Whether the user has registered a platform
        """
        async with UserDatabase() as udb:
            is_linked = await udb.check_if_platform_registered(
                platform, value
            )
            if is_linked is True:
                embed = self.generate_error_embed(
                    header="Look out!",
                    message=f"""It seems like `{value}` is already registered under another user!
If you have any questions, feel free to contact the developer via `/about`.""",
                    is_user_error=True,
                )
                await ctx.send(embed=embed)
                return True
            return False

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

    @member.subcommand(
        sub_cmd_name="register",
        sub_cmd_description="Assist member in registering",
        options=[
            ipy.SlashCommandOption(
                name="user",
                description="User to register",
                type=ipy.OptionType.USER,
                required=True,
            ),
            ipy.SlashCommandOption(
                name="mal_username",
                description="User's MyAnimeList username",
                type=ipy.OptionType.STRING,
                required=True,
            ),
        ],
    )
    async def serversettings_member_register(
        self,
        ctx: ipy.SlashContext,
        user: ipy.Member,
        mal_username: str,
    ):
        """
        Register a member

        Args:
            user (ipy.Member): Member to register
            mal_username (str): User's MyAnimeList username
        """
        await ctx.defer(ephemeral=True)
        checker = await self._check_if_registered(ctx, user)
        if checker is True:
            await ctx.send(
                f"{EMOJI_FORBIDDEN} {user.mention} is already registered!")
            return
        fields = [
            ipy.EmbedField(
                name="0. Ask user to read bot's privacy policy",
                value=f"You must ask {user.mention} to read the bot's privacy policy [here](https://github.com/nattadasu/ryuuRyuusei/blob/main/PRIVACY.md).",
            ),
            ipy.EmbedField(
                name="1. Sign in to MyAnimeList",
                value=f"Ask {user.mention} to sign in to their MyAnimeList account on their default browser",
            ),
            ipy.EmbedField(
                name="2. Go to profile settings",
                value="Once user signed in, ask user to open profile settings. [Click here to go to profile settings](https://myanimelist.net/editprofile.php).",
            ),
            ipy.EmbedField(
                name='3. Scroll down to "My Details" and find "Location"',
                value="User can modify their location later once registration completed.",
            ),
        ]

        overwrite_prompt = "4. Copy the following text and ask user to overwrite/paste it into the Location field"

        with Verificator() as verify:
            # check if user still have pending verification
            verification = verify.get_user_uuid(user.id)
            if verification is not None:
                remaining_time = verification.epoch_time + 43200
            else:
                verification = verify.save_user_uuid(user.id, mal_username)
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
                name="5. Ask user to save the changes",
                value="Once they finished, confirm their registration by typing `/serversettings member verify`.",
            ),
        ]
        embed = ipy.Embed(
            title="Registration",
            description=f"""To assist registration for {user.mention}, please follow the instructions below:""",
            footer=ipy.EmbedFooter(
                text="If you have any questions, feel free to contact the developer. Verification codes are valid for 12 hours.",
            ),
            timestamp=epoch,
            color=0x7289DA,
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_fields(*fields)

        await ctx.send(embed=embed)

    @member.subcommand(
        sub_cmd_name="verify",
        sub_cmd_description="Verify member registration",
        options=[
            ipy.SlashCommandOption(
                name="user",
                description="User to verify",
                type=ipy.OptionType.USER,
                required=True,
            ),
        ],
    )
    async def serversettings_member_verify(
        self, ctx: ipy.ComponentContext, user: ipy.Member
    ):
        """
        Verify a member

        Args:
            user (ipy.Member): Member to verify
        """
        await ctx.defer(ephemeral=True)

        guild = ctx.guild

        if guild is None:
            await ctx.send(
                f"{EMOJI_FORBIDDEN} This command can only be used in a server!")
            return

        guild_id = guild.id
        guild_name = guild.name

        checker = await self._check_if_registered(ctx, user)
        if checker is True:
            return
        # check if user location matches the generated uuid
        with Verificator() as verify:
            user_code = verify.get_user_uuid(user.id)
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
                message=f"Location on {user.mention} profile does not match the generated code. Please try again.",
                is_user_error=True,
            )
            await ctx.send(embed=embed)
            return

        async with UserDatabase() as udb:
            await udb.save_to_database(
                UserDatabaseClass(
                    discord_id=user.id,
                    discord_username=user.username,
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
            message=f"{user.mention} have been registered!",
        )
        cache_ = Caching("cache/verify", 43200)
        path = f"{user.id}.json"
        file_path = cache_.get_cache_path(path)
        await ctx.send(embed=embed)
        cache_.drop_cache(file_path)
        return


def setup(bot: ipy.Client | ipy.AutoShardedClient):
    """Setup function for server settings cog"""
    ServerSettings(bot)
