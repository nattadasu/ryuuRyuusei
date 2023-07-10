"""
Automatically send a media (anime, manga, games, movie, tv) embed info
to a channel when a message is sent with a link to a supported site.
"""
import aiohttp
import interactions as ipy
import regex_spm
from interactions.api.events import MessageCreate

from modules.anilist import anilist_submit
from modules.myanimelist import mal_submit
from modules.simkl import simkl_submit
from modules.rawg import rawg_submit
from modules.commons import save_traceback_to_file
from classes.animeapi import AnimeApi
from classes.anilist import AniList
from classes.simkl import Simkl


class MessageListen(ipy.Extension):
    """Listens for messages with links to supported sites."""

    @ipy.listen(MessageCreate)
    async def on_message_create(self, event: MessageCreate) -> None:
        """Send a media embed if a supported link is sent."""
        ctx = event.message
        if ctx.author.id == self.bot.user.id:
            return
        if ctx.author.bot:
            return
        msg_content = ctx.content
        # find hyperlink in message
        try:
            match regex_spm.match_in(msg_content):
                case r"(https?://)?(www\.)?myanimelist\.net/anime/(?P<mediaid>\d+)" as ids:
                    mal_id: int = ids['mediaid']
                    await mal_submit(ctx, mal_id)
                case r"(https?://)?(www\.)?myanimelist\.net/manga/(?P<mediaid>\d+)" as ids:
                    # resolve manga id to AniList id
                    mal_id: int = ids['mediaid']
                    async with AniList() as anilist:
                        al_id = await anilist.manga(mal_id, from_mal=True)
                    await anilist_submit(ctx, al_id)
                case r"(https?://)?(www\.)?anilist\.co/anime/(?P<mediaid>\d+)" as ids:
                    # get MAL ID from AnimeAPI
                    al_id: int = ids['mediaid']
                    async with AnimeApi() as aapi:
                        aapi_dat = await aapi.get_relation(
                            al_id,
                            aapi.AnimeApiPlatforms.ANILIST)
                        mal_id = aapi_dat.myanimelist
                    if mal_id is None:
                        return
                    await mal_submit(ctx, mal_id)
                case r"(https?://)?(www\.)?anilist\.co/manga/(?P<mediaid>\d+)" as ids:
                    al_id: int = ids['mediaid']
                    await anilist_submit(ctx, al_id)
                case r"(https?://)?(www\.)?simkl\.com/anime/(?P<mediaid>\d+)" as ids:
                    simkl_id: int = ids['mediaid']
                    async with Simkl() as simkl:
                        simkl_dat = await simkl.get_title_ids(simkl_id, 'anime')
                    mal_id = simkl_dat.mal
                    if mal_id is None:
                        return
                    await mal_submit(ctx, int(mal_id))
                case r"(https?://)?(www\.)?simkl\.com/tv/(?P<mediaid>\d+)" as ids:
                    simkl_id: int = ids['mediaid']
                    await simkl_submit(ctx, simkl_id, 'tv')
                case r"(https?://)?(www\.)?simkl\.com/movies/(?P<mediaid>\d+)" as ids:
                    simkl_id: int = ids['mediaid']
                    await simkl_submit(ctx, simkl_id, 'movies')
                case r"(https?://)?(www\.)?rawg\.io/games/(?P<mediaid>[\w-]+)" as ids:
                    rawg_slug: str = ids['mediaid']
                    await rawg_submit(ctx, rawg_slug)
                # kitsu anime
                case r"(https?://)?(www\.)?kitsu\.io/anime/(?P<mediaid>[\w\-]+)" as ids:
                    kitsu_id: str = ids['mediaid']
                    if not kitsu_id.isdigit():
                        async with aiohttp.ClientSession() as sess:
                            async with sess.get(f"https://kitsu.io/api/edge/anime?filter[slug]={kitsu_id}") as resp:
                                if resp.status != 200:
                                    return
                                kitsu_dat = await resp.json()
                                kitsu_id = kitsu_dat['data'][0]['id']
                    async with AnimeApi() as aapi:
                        aapi_dat = await aapi.get_relation(
                            kitsu_id,
                            aapi.AnimeApiPlatforms.KITSU)
                        mal_id = aapi_dat.myanimelist
                    if mal_id is None:
                        return
                    await mal_submit(ctx, mal_id)
                # animeplanet anime
                case r"(https?://)?(www\.)?anime-planet\.com/anime/(?P<mediaid>[\w\-]+)" as ids:
                    ap_id: str = ids['mediaid']
                    async with AnimeApi() as aapi:
                        aapi_dat = await aapi.get_relation(
                            ap_id,
                            aapi.AnimeApiPlatforms.ANIMEPLANET)
                        mal_id = aapi_dat.myanimelist
                    if mal_id is None:
                        return
                    await mal_submit(ctx, mal_id)
                # anidb anime
                case r"(https?://)?(www\.)?anidb\.net/anime/(?P<mediaid>\d+)" as ids:
                    anidb_id: str = ids['mediaid']
                    async with AnimeApi() as aapi:
                        aapi_dat = await aapi.get_relation(
                            anidb_id,
                            aapi.AnimeApiPlatforms.ANIDB)
                        mal_id = aapi_dat.myanimelist
                    if mal_id is None:
                        return
                    await mal_submit(ctx, mal_id)
                # shikimori anime
                case r"(https?://)?(www\.)?shikimori\.one/animes/(?P<mediaid>\w+)" as ids:
                    shikimori_id: str = ids['mediaid']
                    # remove all non-numeric characters
                    shikimori_id = ''.join(
                        filter(str.isdigit, shikimori_id))
                    await mal_submit(ctx, int(shikimori_id))
                # shikimori manga
                case r"(https?://)?(www\.)?shikimori\.one/mangas/(?P<mediaid>\w+)" as ids:
                    shikimori_id: str = ids['mediaid']
                    # remove all non-numeric characters
                    shikimori_id = ''.join(
                        filter(str.isdigit, shikimori_id))
                    async with AniList() as anilist:
                        al_id = await anilist.manga(shikimori_id, from_mal=True)
                    await anilist_submit(ctx, al_id)
                # anime-planet anime
                case r"(https?://)?(www\.)?anime-planet\.com/anime/(?P<mediaid>[\w\-]+)" as ids:
                    ap_id: str = ids['mediaid']
                    async with AnimeApi() as aapi:
                        aapi_dat = await aapi.get_relation(
                            ap_id,
                            aapi.AnimeApiPlatforms.ANIMEPLANET)
                        mal_id = aapi_dat.myanimelist
                    if mal_id is None:
                        return
                    await mal_submit(ctx, mal_id)
                # anisearch anime
                case r"(https?://)?(www\.)?anisearch\.com/anime/(?P<mediaid>\d+)" as ids:
                    anisearch_id: str = ids['mediaid']
                    async with AnimeApi() as aapi:
                        aapi_dat = await aapi.get_relation(
                            anisearch_id,
                            aapi.AnimeApiPlatforms.ANISEARCH)
                        mal_id = aapi_dat.myanimelist
                    if mal_id is None:
                        return
                    await mal_submit(ctx, mal_id)
                # annict anime
                case r"(https?://)?(en\.|www\.)?annict\.com/works/(?P<mediaid>\d+)" as ids:
                    annict_id: str = ids['mediaid']
                    async with AnimeApi() as aapi:
                        aapi_dat = await aapi.get_relation(
                            annict_id,
                            aapi.AnimeApiPlatforms.ANNICT)
                        mal_id = aapi_dat.myanimelist
                    if mal_id is None:
                        return
                    await mal_submit(ctx, mal_id)
                # kaize anime
                # example: https://kaize.io/anime/jujutsu-kaisen-2nd-season
                case r"(https?://)?(www\.)?kaize\.io/anime/(?P<mediaid>[\w\-]+)" as ids:
                    kaize_slug: str = ids['mediaid']
                    async with AnimeApi() as aapi:
                        aapi_dat = await aapi.get_relation(
                            kaize_slug,
                            aapi.AnimeApiPlatforms.KAIZE)
                        mal_id = aapi_dat.myanimelist
                    if mal_id is None:
                        return
                    await mal_submit(ctx, mal_id)
                # livechart anime
                case r"(https?://)?(www\.)?livechart\.me/anime/(?P<mediaid>\d+)" as ids:
                    livechart_id: str = ids['mediaid']
                    async with AnimeApi() as aapi:
                        aapi_dat = await aapi.get_relation(
                            livechart_id,
                            aapi.AnimeApiPlatforms.LIVECHART)
                        mal_id = aapi_dat.myanimelist
                    if mal_id is None:
                        return
                    await mal_submit(ctx, mal_id)
                # notify.moe anime
                # id uses URI-safe Base64
                case r"(https?://)?(www\.)?notify\.moe/anime/(?P<mediaid>[\w\-_]+)" as ids:
                    notify_id: str = ids['mediaid']
                    async with AnimeApi() as aapi:
                        aapi_dat = await aapi.get_relation(
                            notify_id,
                            aapi.AnimeApiPlatforms.NOTIFY)
                        mal_id = aapi_dat.myanimelist
                    if mal_id is None:
                        return
                    await mal_submit(ctx, mal_id)
                # otak otaku anime
                case r"(https?://)?(www\.)?otakotaku\.com/anime/view/(?P<mediaid>\d+)" as ids:
                    otakotaku_id: str = ids['mediaid']
                    async with AnimeApi() as aapi:
                        aapi_dat = await aapi.get_relation(
                            otakotaku_id,
                            aapi.AnimeApiPlatforms.OTAKOTAKU)
                        mal_id = aapi_dat.myanimelist
                    if mal_id is None:
                        return
                    await mal_submit(ctx, mal_id)
                # silveryasha anime
                # example: https://db.silveryasha.web.id/anime/278
                case r"(https?://)?(www\.)?db\.silveryasha\.web\.id/anime/(?P<mediaid>\d+)" as ids:
                    silveryasha_id: str = ids['mediaid']
                    async with AnimeApi() as aapi:
                        aapi_dat = await aapi.get_relation(
                            silveryasha_id,
                            aapi.AnimeApiPlatforms.SILVERYASHA)
                        mal_id = aapi_dat.myanimelist
                    if mal_id is None:
                        return
                    await mal_submit(ctx, mal_id)
                case _:
                    return
        except Exception as err:
            save_traceback_to_file(
                "events_message_create",
                ctx.author,
                err,
                mute_error=True,
            )

def setup(bot: ipy.Client | ipy.AutoShardedClient) -> None:
    """Load the extension."""
    MessageListen(bot)
