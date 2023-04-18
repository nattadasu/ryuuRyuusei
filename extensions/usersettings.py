import interactions as ipy
from modules.i18n import paginateLanguage, setLanguage, searchLanguage
from modules.const import EMOJI_SUCCESS, EMOJI_FORBIDDEN
from emoji import emojize


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
        name="lang",
        description="Language code",
        required=True,
        opt_type=ipy.OptionType.STRING,
        autocomplete=True,
    )
    async def usersettings_language_set(self, ctx: ipy.InteractionContext, lang: str):
        try:
            await setLanguage(code=lang, ctx=ctx, isGuild=False)
            await ctx.send(f"{EMOJI_SUCCESS} Language set to {lang}", ephemeral=True)
        except Exception as e:
            await ctx.send(f"{EMOJI_FORBIDDEN} {e}")

    @usersettings_language_set.autocomplete("lang")
    async def code_autocomplete(self, ctx: ipy.AutocompleteContext):
        data = searchLanguage(ctx.input_text)
        # only return the first 10 results
        data = data[:10]
        final = []
        for di in data:
            try:
                if di['name'] == 'Serbian':
                    di['dialect'] = 'Serbia'
                flag = di['dialect'].replace(' ', '_')
                flag = emojize(f":{flag}:", language="alias")
                final.append({
                    'name': f"{flag} {di['name']} ({di['native']}, {di['dialect']})",
                    'value': di['code']
                })
            except:
                break
        await ctx.send(choices=final)


def setup(bot):
    UserSettings(bot)