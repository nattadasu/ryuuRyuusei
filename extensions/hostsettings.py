import re

import interactions as ipy

from classes.database import UserDatabase
from modules.const import (AUTHOR_USERID, EMOJI_SUCCESS,
                           EMOJI_UNEXPECTED_ERROR, EMOJI_USER_ERROR,
                           VERIFICATION_SERVER, VERIFIED_ROLE)
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
        name="member",
        description="Manage member settings, for self-hosted bot only")

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

        user_roles = [str(role.id)
                      for role in ctx.author.roles]  # type: ignore

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


def setup(bot: ipy.Client):
    HostSettings(bot)
