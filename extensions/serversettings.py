import os
import re
from datetime import datetime, timezone

import interactions as ipy
from emoji import emojize

from classes.database import UserDatabase, UserDatabaseClass
from classes.html.myanimelist import HtmlMyAnimeList
from classes.verificator import Verificator
from modules.const import (
    EMOJI_FORBIDDEN,
    EMOJI_SUCCESS,
    EMOJI_UNEXPECTED_ERROR,
    EMOJI_USER_ERROR,
    VERIFICATION_SERVER,
    VERIFIED_ROLE,
)
from modules.i18n import search_language, set_default_language


class ServerSettings(ipy.Extension):
    """Server Settings commands"""

    def __init__(self, bot: ipy.AutoShardedClient):
        self.bot = bot

    @ipy.slash_command(
        name="serversettings",
        description="Change the bot settings",
        default_member_permissions=ipy.Permissions.ADMINISTRATOR,
        dm_permission=False,
    )
    async def serversettings(self, ctx: ipy.InteractionContext):
        pass

    @serversettings.subcommand(
        group_name="language",
        group_description="Change the bot language",
        sub_cmd_name="set",
        sub_cmd_description="Set the bot language for this server",
    )
    @ipy.slash_option(
        name="lang",
        description="Language name",
        required=True,
        opt_type=ipy.OptionType.STRING,
        autocomplete=True,
    )
    async def serversettings_language_set(self, ctx: ipy.InteractionContext, lang: str):
        try:
            await set_default_language(code=lang, ctx=ctx, isGuild=True)
            await ctx.send(f"{EMOJI_SUCCESS} Server Language set to {lang}")
        except Exception as e:
            await ctx.send(f"{EMOJI_FORBIDDEN} {e}")

    @serversettings_language_set.autocomplete("lang")
    async def code_autocomplete(self, ctx: ipy.AutocompleteContext):
        data = search_language(ctx.input_text)
        # only return the first 10 results
        data = data[:10]
        final = []
        for di in data:
            try:
                if di["name"] == "Serbian":
                    di["dialect"] = "Serbia"
                flag = di["dialect"].replace(" ", "_")
                flag = emojize(f":{flag}:", language="alias")
                final.append(
                    {
                        "name": f"{flag} {di['name']} ({di['native']}, {di['dialect']})",
                        "value": di["code"],
                    }
                )
            except BaseException:
                break
        await ctx.send(choices=final)

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
        async with UserDatabase() as ud:
            is_registered = await ud.check_if_registered(user.id)
            if is_registered is True:
                embed = self.generate_error_embed(
                    header="Look out!",
                    message="User is already registered!",
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

    @serversettings.subcommand(
        group_name="member",
        group_description="Manage member settings",
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
        user: ipy.Member | ipy.User,
        mal_username: str,
    ):
        await ctx.defer(ephemeral=True)
        checker = await self._check_if_registered(ctx, user)
        if checker is True:
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
            is_pending = verify.get_user_uuid(user.id)
            if is_pending is not None:
                remaining_time = is_pending.epoch_time + 43200
                fields.append(
                    ipy.EmbedField(
                        name=overwrite_prompt,
                        value=f"```\n{is_pending.uuid}\n```**Note:** Verification code expires <t:{remaining_time}:R>.",
                    )
                )
                epoch = datetime.fromtimestamp(is_pending.epoch_time, tz=timezone.utc)
            else:
                generate = verify.save_user_uuid(user.id, mal_username)
                remaining_time = generate.epoch_time + 43200
                fields.append(
                    ipy.EmbedField(
                        name=overwrite_prompt,
                        value=f"```\n{generate.uuid}\n```**Note:** Verification code expires <t:{remaining_time}:R>.",
                    )
                )
                epoch = datetime.fromtimestamp(generate.epoch_time, tz=timezone.utc)

        fields += [
            ipy.EmbedField(
                name="5. Ask user to save the changes",
                value="Once they finished, confirm their registration by typing `/serversettings member verify`.",
            ),
        ]
        embed = ipy.Embed(
            title="Registration",
            description=f"""To assist registration for {user.mention}, please follow the instructions below:""",
            fields=fields,
            footer=ipy.EmbedFooter(
                text="If you have any questions, feel free to contact the developer. Verification codes are valid for 12 hours.",
            ),
            timestamp=epoch,
            color=0x7289DA,
        )
        embed.set_thumbnail(url=user.display_avatar.url)

        await ctx.send(embed=embed)

    @serversettings.subcommand(
        group_name="member",
        group_description="Manage member settings",
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
        self, ctx: ipy.ComponentContext, user: ipy.Member | ipy.User
    ):
        await ctx.defer(ephemeral=True)
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

        async with UserDatabase() as ud:
            await ud.save_to_database(
                UserDatabaseClass(
                    discord_id=user.id,
                    discord_username=user.username,
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
            message=f"{user.mention} have been registered!",
        )
        directory = "cache/verify"
        path = f"{ctx.author.id}_{user.id}.json"
        await ctx.send(embed=embed)
        file_path = os.path.join(directory, path)
        os.remove(file_path)

    @serversettings.subcommand(
        group_name="member",
        group_description="Manage member settings",
        sub_cmd_name="verify_club",
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
    async def serversettings_member_verify_club(
        self, ctx: ipy.SlashContext, user: ipy.Member | ipy.User
    ):
        await ctx.defer(ephemeral=True)
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

        user_roles = [str(role.id) for role in ctx.author.roles]

        # check if verified role exists
        if status is True and str(VERIFIED_ROLE) not in user_roles:
            await ctx.member.add_role(
                VERIFIED_ROLE,
                reason=f"User verified via slash command by {ctx.author.username}#{ctx.author.discriminator} ({ctx.author.id})",
            )
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


def setup(bot):
    ServerSettings(bot)
