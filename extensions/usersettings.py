import interactions as ipy
from modules.i18n import paginateLanguage, setLanguage
from modules.const import EMOJI_SUCCESS, EMOJI_FORBIDDEN


class UserSettings(ipy.Extension):
    @ipy.slash_command(
        name="usersettings",
        description="Change the bot settings",
    )
    async def usersettings(self, ctx: ipy.InteractionContext):
        pass

    @usersettings.subcommand(
        group_name="language",
        group_description="Change the bot language",
        sub_cmd_name="list",
        sub_cmd_description="List the available languages",
    )
    async def usersettings_language_list(self, ctx: ipy.InteractionContext):
        await paginateLanguage(bot=self.bot, ctx=ctx)

    @usersettings.subcommand(
        group_name="language",
        group_description="Change the bot language",
        sub_cmd_name="set",
        sub_cmd_description="Set the bot language",
    )
    @ipy.slash_option(
        name="code",
        description="Language code",
        required=True,
        opt_type=ipy.OptionType.STRING,
    )
    async def usersettings_language_set(self, ctx: ipy.InteractionContext, code: str):
        try:
            await setLanguage(code=code, ctx=ctx, isGuild=False)
            await ctx.send(f"{EMOJI_SUCCESS} Language set to {code}", ephemeral=True)
        except Exception as e:
            await ctx.send(f"{EMOJI_FORBIDDEN} {e}")


def setup(bot):
    UserSettings(bot)
