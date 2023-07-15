import os

import interactions as ipy
from emoji import emojize

from modules.commons import save_traceback_to_file
from modules.const import EMOJI_FORBIDDEN, EMOJI_SUCCESS
from modules.i18n import (paginate_language, search_language,
                          set_default_language)


class UserSettings(ipy.Extension):
    """User Settings commands"""

    usersettings_head = ipy.SlashCommand(
        name="usersettings",
        description="Change the bot settings",
        dm_permission=True,
        cooldown=ipy.Cooldown(
            cooldown_bucket=ipy.Buckets.USER,
            rate=1,
            interval=5,
        ),
    )

    language = usersettings_head.group(
        name="language",
        description="Change the bot language",
    )
    
    @usersettings_head.subcommand(
        sub_cmd_name="autoembed",
        sub_cmd_description="Configure autoembed function",
        options=[
            ipy.SlashCommandOption(
                name="state",
                description="Enable/disable function",
                type=ipy.OptionType.STRING,
                required=True,
                choices=[
                    ipy.SlashCommandChoice(
                        name="Enable",
                        value="true",
                    ),
                    ipy.SlashCommandChoice(
                        name="Disable",
                        value="false",
                    ),
                ],
            ),
        ],
    )
    async def usersettings_autoembed(self, ctx: ipy.SlashContext, state: str):
        """Enable or disable autoembed"""
        file_path = f"database/allowlist_autoembed/{ctx.author.id}"
        path_exist = os.path.exists(file_path)
        state_ = "true" == state
        if path_exist and state_ is True:
            await ctx.send("It seems you've enabled the feature already. If you wanted to disable, set `state` to `disable`", ephemeral=True)
            return
        if not path_exist and state_ is False:
            await ctx.send("It seems you've disabled the feature already. If you wanted to enable, set `state` to `enable`", ephemeral=True)
            return
        
        if state_:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write("")
            await ctx.send("""Feature enabled, now Ryuusei will automatically respond to your message with supported sites.

We currently support following sites
## Anime
*Uses MyAnimeList for information*
AniList, aniDB, Anime-Planet, aniSearch, Annict, Kaize, Kitsu, LiveChart, MyAnimeList, Notify.moe, Otak-Otaku, Shikimori, Database Tontonan Indonesia Silver Yasha
## Manga
*Uses AniList for information*
AniList, Kitsu, MangaDex (+ chapter), MyAnimeList, Shikimori
Upcoming: Kaize
## Movies and TV Shows
*Uses SIMKL for information*
SIMKL
Upcoming: IMDb, TMDB, Trakt
## Games
*Uses RAWG*
RAWG""", ephemeral=True)
            return
    
        os.remove(file_path)
        await ctx.send("Feature disabled.", ephemeral=True)

    @usersettings_head.subcommand(
        group_name="language",
        group_description="Change the bot language",
        sub_cmd_name="list",
        sub_cmd_description="List the available languages",
    )
    async def usersettings_language_list(self, ctx: ipy.InteractionContext):
        await paginate_language(bot=self.bot, ctx=ctx)

    @usersettings_head.subcommand(
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
            await set_default_language(code=lang, ctx=ctx, isGuild=False)
            await ctx.send(f"{EMOJI_SUCCESS} Language set to {lang}", ephemeral=True)
        except Exception as e:
            await ctx.send(f"{EMOJI_FORBIDDEN} {e}")
            save_traceback_to_file("usersettings_language_set", ctx.author, e)

    @usersettings_language_set.autocomplete("lang")
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


def setup(bot):
    UserSettings(bot)
