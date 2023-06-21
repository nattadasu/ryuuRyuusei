import interactions as ipy

from classes.database import UserDatabase
from modules.const import AUTHOR_USERID, VERIFICATION_SERVER, VERIFIED_ROLE
from modules.discord import format_username


class HostSettings(ipy.Extension):
    """Host Settings commands"""

    hostsettings_head = ipy.SlashCommand(
        name="hostsettings",
        description="Change the bot settings, for self-hosted bot only",
        scopes=[
            AUTHOR_USERID,
            VERIFICATION_SERVER,
        ],
        dm_permission=False,
    )

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
                reason=f"User verified via slash command by {format_username(ctx.author)} ({ctx.author.id})",
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
    HostSettings(bot)
