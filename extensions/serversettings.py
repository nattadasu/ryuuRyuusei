# File: `serversettings.py`

import interactions as ipy
from modules.i18n import setLanguage
from modules.const import EMOJI_SUCCESS, EMOJI_FORBIDDEN


class ServerSettings(ipy.Extension):
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
        sub_cmd_name="server",
        sub_cmd_description="Set the bot language for this server",
    )
    @ipy.slash_option(
        name="code",
        description="Language code, check from /usersettings language list",
        required=True,
        opt_type=ipy.OptionType.STRING,
    )
    async def serversettings_language_set(self, ctx: ipy.InteractionContext, code: str):
        try:
            await setLanguage(code=code, ctx=ctx, isGuild=True)
            await ctx.send(f"{EMOJI_SUCCESS} Server Language set to {code}")
        except Exception as e:
            await ctx.send(f"{EMOJI_FORBIDDEN} {e}")


def setup(bot):
    ServerSettings(bot)
