import os

import interactions as ipy

from classes import cache
from classes.anilist import AniList
from classes.database import UserDatabase
from classes.jikan import JikanApi
from classes.shikimori import Shikimori

Cache = cache.Caching(
    cache_directory="cache/refresh", cache_expiration_time=60 * 60 * 24
)


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
        sub_cmd_name="refresh_accounts",
        sub_cmd_description="Refresh your account informations",
    )
    async def usersettings_refresh_accounts(self, ctx: ipy.SlashContext):
        """Refresh account informations"""
        await ctx.defer(ephemeral=True)
        cfp = Cache.get_cache_path(f"{ctx.author.id}.json")
        cached: cache.CacheModel | None = Cache.read_cache(cfp, as_raw=True)
        if cached:
            timestamp = cached.timestamp + Cache.cache_expiration_time
            await ctx.send(
                (
                    "You've invoked refresh command recently. "
                    f"You can reinvoke the command <t:{int(timestamp)}:R>"
                ),
                ephemeral=True,
            )
            return

        udb = UserDatabase()
        if not await udb.check_if_registered(ctx.author.id):
            await ctx.send("You haven't register yet.", ephemeral=True)
            return

        usr_ = await udb.get_user_data(ctx.author.id)

        success: list[str] = []
        fails: list[str] = []
        unsupported: list[str] = []
        not_modified: list[str] = []
        try:
            async with JikanApi() as jikan:
                jusr_ = await jikan.get_user_by_id(usr_.mal_id)
            if jusr_.username == usr_.mal_username:
                not_modified.append("MyAnimeList")
            else:
                await udb.update_user(
                    ctx.author.id, row="malUsername", modified_input=jusr_.username
                )
                success.append("MyAnimeList")
        except Exception as _:
            await ctx.send(
                (
                    "Failed to refresh MyAnimeList account by looking up through user ID. "
                    "Please unregister and register again."
                ),
                ephemeral=True,
            )
            return

        if usr_.anilist_id:
            try:
                async with AniList() as al_:
                    ausr_ = await al_.user_by_id(usr_.anilist_id, True)
                if ausr_.name == usr_.anilist_username:
                    not_modified.append("AniList")
                else:
                    await udb.update_user(
                        ctx.author.id, row="anilistUsername", modified_input=ausr_.name
                    )
                    success.append("AniList")
            except Exception as err:
                fails.append(f"AniList (`{err}`)")

        if usr_.lastfm_username:
            unsupported.append("Last.FM")

        if usr_.shikimori_id:
            try:
                async with Shikimori() as shiki:
                    susr_ = await shiki.get_user(usr_.shikimori_id, is_nickname=False)
                if susr_.nickname == usr_.shikimori_username:
                    not_modified.append("Shikimori")
                else:
                    await udb.update_user(
                        ctx.author.id,
                        row="shikimoriUsername",
                        modified_input=susr_.nickname,
                    )
                    success.append("Shikimori")
            except Exception as err:
                fails.append(f"Shikimori (`{err}`)")

        final = "We've refreshed your account informations.\n"
        remarks: list[str] = []
        if success:
            final += f"* Successfully refreshed: {', '.join(success)}\n"
        if fails:
            final += f"* Failed to refresh: {', '.join(fails)}\n"
            remarks.append("failed")
        if unsupported:
            final += f"* Unsupported\\*: {', '.join(unsupported)}\n"
            remarks.append("unsupported")
        if not_modified:
            final += f"* Not modified: {', '.join(not_modified)}\n"
        plurals = [*fails, *unsupported]
        f_p = "s" if len(plurals) > 1 else ""
        if remarks:
            final += f"For {' or '.join(remarks)} account{f_p}, please relink them by `/platform unlink` then `/platform link`"
        if unsupported:
            final += "\n-# \\* Database only stores modifiable identifier, not permanent one like ID number."
        Cache.write_cache(cfp, final)
        await ctx.send(final, ephemeral=True)

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
            await ctx.send(
                "It seems you've enabled the feature already. If you wanted to disable, set `state` to `disable`",
                ephemeral=True,
            )
            return
        if not path_exist and state_ is False:
            await ctx.send(
                "It seems you've disabled the feature already. If you wanted to enable, set `state` to `enable`",
                ephemeral=True,
            )
            return

        if state_:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write("")
            await ctx.send(
                """Feature enabled, now Ryuusei will automatically respond to your message with supported sites.

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
RAWG""",
                ephemeral=True,
            )
            return

        os.remove(file_path)
        await ctx.send("Feature disabled.", ephemeral=True)


def setup(bot: ipy.Client | ipy.AutoShardedClient):
    """Load the extension"""
    UserSettings(bot)
