"""
Automatically send a media (anime, manga, games, movie, tv) embed info
to a channel when a message is sent with a link to a supported site.
"""
import os
import re
from typing import Literal

import aiohttp
import interactions as ipy
import regex_spm
from interactions.api.events import MessageCreate

from classes.anilist import AniList
from classes.animeapi import AnimeApi
from classes.mangadex import Manga, Mangadex
from classes.simkl import Simkl
from modules.anilist import anilist_submit
from modules.commons import save_traceback_to_file
from modules.myanimelist import mal_submit
from modules.rawg import rawg_submit
from modules.simkl import simkl_submit


def intepret_mdx(data: Manga) -> tuple[str, str, str, str]:
    """Get the media ID and source from a MangaDex manga object"""
    mal_id = data.attributes.links.mal
    al_id = data.attributes.links.al
    kt_id = data.attributes.links.kt
    if not mal_id and not al_id and not kt_id:
        return None, None, None, None
    if al_id:
        send_to = "anilist"
        send_type = "manga"
        media_id = al_id
        source = "anilist"
    elif kt_id:
        mal_id = kitsu_id_to_other_id(kt_id, "manga", "anilist")
        if mal_id is None:
            return None, None, None, None
        send_to = "anilist"
        send_type = "manga"
        media_id = mal_id
        source = "myanimelist"
    else:
        send_to = "anilist"
        send_type = "manga"
        media_id = mal_id
        source = "myanimelist"
    return send_to, send_type, media_id, source


async def kitsu_id_to_other_id(
    kitsu_id: str,
    media_kind: Literal["anime", "manga"],
    destination: Literal["anilist", "myanimelist"]
) -> str | None:
    """Convert a Kitsu ID to another ID"""
    if not kitsu_id.isdigit():
        async with aiohttp.ClientSession() as session, session.get(f"https://kitsu.app/api/edge/{media_kind}?filter[slug]={kitsu_id}") as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            kitsu_id = data["data"][0]["id"]
    async with aiohttp.ClientSession() as session, session.get(f"https://kitsu.app/api/edge/{media_kind}/{kitsu_id}/mappings") as resp:
        if resp.status != 200:
            return
        data = await resp.json()
        # find for anilist/manga on data.data[*].attributes.externalSite
        for mapping in data["data"]:
            if mapping["attributes"]["externalSite"] == f"{destination}/{media_kind}":
                return mapping["attributes"]["externalId"]
    return None


class MessageListen(ipy.Extension):
    """Listens for messages with links to supported sites."""

    @ipy.listen(MessageCreate)
    async def on_message_create(self, event: MessageCreate) -> None:
        """Send a media embed if a supported link is sent."""
        ctx = event.message
        if ctx.author.id == self.bot.user.id or ctx.author.bot:
            return

        msg_content = ctx.content
        mentioned = msg_content.startswith(
            f'<@!{self.bot.user.id}>') or msg_content.startswith(f'<@{self.bot.user.id}>')

        # do not process if the message explicitly says not to
        if re.search(r"no bot", msg_content, re.IGNORECASE) or msg_content.startswith("!!"):
            return

        # if the message mentions the bot, send warning
        if mentioned and len(msg_content) <= 30:
            await ctx.reply(
                f"""Hello, {ctx.author.mention}! This bot heavily relies on slash commands.
Please use the slash command `/help` to see a list of commands available.

If you can't see the slash commands, please re-invite the bot to your server, and make sure you have the `applications.commands` scope enabled."""
            )
            return

        if not os.path.exists(f"database/allowlist_autoembed/{ctx.author.id}"):
            return

        send_to: Literal["anilist", "mal", "simkl", "rawg"] | None = None
        send_type: Literal["anime", "manga",
                           "game", "movie", "tv"] | None = None
        media_id: str | None = None
        source: str | None = None
        mdx: Manga | None = None

        match regex_spm.search_in(msg_content):
            case r"(?:https?://)?(?:www\.)?anilist\.co/anime/(?P<mediaid>\d+)" as ids:
                send_to = "mal"
                send_type = "anime"
                media_id = ids["mediaid"]
                source = "anilist"
            case r"(?:https?://)?(?:www\.)?anilist\.co/manga/(?P<mediaid>\d+)" as ids:
                send_to = "anilist"
                send_type = "manga"
                media_id = ids["mediaid"]
                source = "anilist"
            case r"(?:https?://)?(?:www\.)?anidb\.net/(?:anime/|a)(?P<mediaid>\d+)" as ids:
                send_to = "mal"
                send_type = "anime"
                media_id = ids["mediaid"]
                source = "anidb"
            case r"(?:https?://)?(?:www\.)?anime-planet\.com/anime/(?P<mediaid>[\w\-]+)" as ids:
                send_to = "mal"
                send_type = "anime"
                media_id = ids["mediaid"]
                source = "animeplanet"
            case r"(?:https?://)?(?:www\.)?anisearch\.com/anime/(?P<mediaid>\d+)" as ids:
                send_to = "mal"
                send_type = "anime"
                media_id = ids["mediaid"]
                source = "anisearch"
            case r"(?:https?://)?(?:en\.|www\.)?annict\.com/works/(?P<mediaid>\d+)" as ids:
                send_to = "mal"
                send_type = "anime"
                media_id = ids["mediaid"]
                source = "annict"
            case r"(?:https?://)?(?:www\.)?kaize\.io/anime/(?P<mediaid>[\w\-]+)" as ids:
                send_to = "mal"
                send_type = "anime"
                media_id = ids["mediaid"]
                source = "kaize"
            case r"(?:https?://)?(?:www\.)?kitsu\.(?:io|app)/anime/(?P<mediaid>[\w\-]+)" as ids:
                media_id: str = ids["mediaid"]
                if not media_id.isdigit():
                    async with aiohttp.ClientSession() as session, session.get(f"https://kitsu.app/api/edge/anime?filter[slug]={media_id}") as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        media_id = data["data"][0]["id"]
                send_to = "mal"
                send_type = "anime"
                source = "kitsu"
            case r"(?:https?://)?(?:www\.)?kitsu\.(?:io|app)/manga/(?P<mediaid>[\w\-]+)" as ids:
                # try find AniList ID on Kitsu GraphQL API
                ids: dict[str, str]
                media_id: str = ids["mediaid"]
                anilist_id = await kitsu_id_to_other_id(media_id, "manga", "anilist")
                if anilist_id is None:
                    return
                send_to = "anilist"
                send_type = "manga"
                media_id = anilist_id
                source = "anilist"
            case r"(?:https?://)?(?:www\.)?livechart\.me/anime/(?P<mediaid>[\w\-]+)" as ids:
                send_to = "mal"
                send_type = "anime"
                media_id = ids["mediaid"]
                source = "livechart"
            case r"(?:https?://)?(?:www\.)?myanimelist\.net/anime/(?P<mediaid>\d+)" as ids:
                send_to = "mal"
                send_type = "anime"
                media_id = ids["mediaid"]
                source = "myanimelist"
            case r"(?:https?://)?myani\.li/#/anime/details/(?P<mediaid>\d+)" as ids:
                send_to = "mal"
                send_type = "anime"
                media_id = ids["mediaid"]
                source = "myanimelist"
            case r"(?:https?://)?(?:www\.)?myanimelist\.net/manga/(?P<mediaid>\d+)" as ids:
                send_to = "anilist"
                send_type = "manga"
                media_id = ids["mediaid"]
                source = "myanimelist"
            case r"(?:https?://)?(?:www\.)?nautiljon\.com/animes/(?P<mediaid>[\w\W]).html" as ids:
                send_to = "mal"
                send_type = "anime"
                media_id = ids["mediaid"]
                source = "nautiljon"
            case r"(?:https?://)?(?:www\.)?notify\.moe/anime/(?P<mediaid>[\w\-_]+)" as ids:
                send_to = "mal"
                send_type = "anime"
                media_id = ids["mediaid"]
                source = "notify"
            case r"(?:https?://)?(?:www\.)?otakotaku\.com/anime/view/(?P<mediaid>[\w\-]+)" as ids:
                send_to = "mal"
                send_type = "anime"
                media_id = ids["mediaid"]
                source = "otakotaku"
            case r"(?:https?://)?(?:www\.)?rawg\.io/games/(?P<mediaid>[\w\-]+)" as ids:
                send_to = "rawg"
                send_type = "game"
                media_id = ids["mediaid"]
                source = "rawg"
            case r"(?:https?://)?(?:www\.)?shikimori\.(one|me|org)/animes/(?P<mediaid>\d+)" as ids:
                send_to = "mal"
                send_type = "anime"
                media_id = ids["mediaid"]
                if not media_id.isdigit():
                    # remove prefix
                    media_id = media_id[1:]
                source = "myanimelist"
            case r"(?:https?://)?(?:www\.)?shikimori\.(one|me|org)/ranobe/(?P<mediaid>\d+)" as ids:
                send_to = "anilist"
                send_type = "manga"
                media_id = ids["mediaid"]
                if not media_id.isdigit():
                    # remove prefix
                    media_id = media_id[1:]
                source = "myanimelist"
            case r"(?:https?://)?(?:www\.)?shikimori\.(one|me|org)/mangas/(?P<mediaid>\d+)" as ids:
                send_to = "anilist"
                send_type = "manga"
                media_id = ids["mediaid"]
                if not media_id.isdigit():
                    # remove prefix
                    media_id = media_id[1:]
                source = "myanimelist"
            case r"(?:https?://)?db.silveryasha\.web\.id/anime/(?P<mediaid>[\w\-]+)" as ids:
                send_to = "mal"
                send_type = "anime"
                media_id = ids["mediaid"]
                source = "silveryasha"
            case r"(?:https?://)?(?:www\.)?simkl\.com/anime/(?P<mediaid>\d+)" as ids:
                async with Simkl() as simkl:
                    smk_dat = await simkl.get_title_ids(ids["mediaid"], "anime")
                    media_id = smk_dat.mal
                    send_to = "mal"
                    send_type = "anime"
                    source = "myanimelist"
            case r"(?:https?://)?(?:www\.)?simkl\.com/movies/(?P<mediaid>\d+)" as ids:
                send_to = "simkl"
                send_type = "movie"
                media_id = ids["mediaid"]
                source = "simkl"
            case r"(?:https?://)?(?:www\.)?simkl\.com/tv/(?P<mediaid>\d+)" as ids:
                send_to = "simkl"
                send_type = "tv"
                media_id = ids["mediaid"]
                source = "simkl"
            # mangadex manga
            case r"(?:https?://)?(?:www\.)?mangadex\.org/title/(?P<mediaid>[\w\-]+)" as ids:
                async with Mangadex() as mdex:
                    mdx = await mdex.get_manga(ids["mediaid"])
                    send_to, send_type, media_id, source = intepret_mdx(mdx)
            # mangadex chapter
            case r"(?:https?://)?(?:www\.)?mangadex\.org/chapter/(?P<chapterid>[\w\-]+)" as ids:
                async with Mangadex() as mdex:
                    mdx = await mdex.get_manga_from_chapter(ids["chapterid"])
                    send_to, send_type, media_id, source = intepret_mdx(mdx)
            case _:
                return

        if send_to is None or media_id is None or source is None:
            return

        try:
            match send_to:
                case "anilist":
                    reverse_lookup = source == "myanimelist"
                    if source != "anilist":
                        async with AniList() as als:
                            aldat = await als.manga(media_id, reverse_lookup)
                            media_id = aldat.id
                    await anilist_submit(ctx, int(media_id))
                case "mal":
                    is_it_source = source == "myanimelist"
                    if is_it_source is False:
                        async with AnimeApi() as aapi:
                            aadat = await aapi.get_relation(media_id, source)
                            media_id = aadat.myanimelist
                            if media_id is None:
                                return
                    await mal_submit(ctx, int(media_id))
                case "simkl":
                    await simkl_submit(ctx, media_id, send_type)
                case "rawg":
                    await rawg_submit(ctx, media_id)
                case _:
                    return
        # pylint: disable=broad-exception-caught
        except Exception as err:
            save_traceback_to_file(
                "message_listen",
                ctx.author,
                err
            )
        return


def setup(bot: ipy.Client | ipy.AutoShardedClient) -> None:
    """Load the extension."""
    MessageListen(bot)
