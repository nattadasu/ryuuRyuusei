import os

import interactions as ipy


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


def setup(bot: ipy.Client | ipy.AutoShardedClient):
    """Load the extension"""
    UserSettings(bot)
