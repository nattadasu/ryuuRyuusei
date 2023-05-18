import interactions as ipy
from emoji import emojize

from modules.const import EMOJI_FORBIDDEN, EMOJI_SUCCESS
from modules.i18n import search_language, set_default_language


class ServerSettings(ipy.Extension):
    """Server Settings commands"""

    def __init__(self, bot: ipy.Client):
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
                        # 'name': flag + " " + di['name'] + " (" + di['native'] + ", " + di['dialect'] + ")",
                        "name": f"{flag} {di['name']} ({di['native']}, {di['dialect']})",
                        "value": di["code"],
                    }
                )
            except BaseException:
                break
        await ctx.send(choices=final)


def setup(bot):
    ServerSettings(bot)
