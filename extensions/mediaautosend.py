"""
Automatically send a media (anime, manga, games, movie, tv) embed info
to a channel when a message is sent with a link to a supported site.
"""
from typing import Literal

import aiohttp
import interactions as ipy
import regex_spm
from interactions.api.events import MessageCreate

from classes.anilist import AniList
from classes.animeapi import AnimeApi
from classes.simkl import Simkl
from modules.anilist import anilist_submit
from modules.commons import save_traceback_to_file
from modules.myanimelist import mal_submit
from modules.rawg import rawg_submit
from modules.simkl import simkl_submit


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

        # if the message mentions the bot, send warning
        if mentioned and len(msg_content) <= 30:
            await ctx.reply(
                f"""Hello, {ctx.author.mention}! This bot heavily relies on slash commands.
Please use the slash command `/help` to see a list of commands available.

If you can't see the slash commands, please re-invite the bot to your server, and make sure you have the `applications.commands` scope enabled."""
            )
            return

        send_to: Literal["anilist", "mal", "simkl", "rawg"] | None = None
        send_type: Literal["anime", "manga",
                           "game", "movie", "tv"] | None = None
        media_id: str | None = None
        source: str | None = None

        match regex_spm.match_in(msg_content):
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
            case r"(?:https?://)?(?:www\.)?anidb\.net/anime/(?P<mediaid>\d+)" as ids:
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
            case r"(?:https?://)?(?:www\.)?kaize\.io/anime/(?P<mediaid>\d+)" as ids:
                send_to = "mal"
                send_type = "anime"
                media_id = ids["mediaid"]
                source = "kaize"
            case r"(?:https?://)?(?:www\.)?kitsu\.io/anime/(?P<mediaid>[\w\-]+)" as ids:
                media_id: str = ids["mediaid"]
                if not media_id.isdigit():
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f"https://kitsu.io/api/edge/anime?filter[slug]={media_id}") as resp:
                            if resp.status != 200:
                                return
                            data = await resp.json()
                            media_id = data["data"][0]["id"]
                send_to = "mal"
                send_type = "anime"
                source = "kitsu"
            case r"(?:https?://)?(?:www\.)?kitsu\.io/manga/(?P<mediaid>[\w\-]+)" as ids:
                # try find AniList ID on Kitsu GraphQL API
                ids: dict[str, str]
                media_id: str = ids["mediaid"]
                if not media_id.isdigit():
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f"https://kitsu.io/api/edge/manga?filter[slug]={media_id}") as resp:
                            if resp.status != 200:
                                return
                            data = await resp.json()
                            media_id = data["data"][0]["id"]
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://kitsu.io/api/edge/manga/{media_id}/mappings") as resp:
                        if resp.status != 200:
                            return
                        data = await resp.json()
                        # find for anilist/manga on data.data[*].attributes.externalSite
                        for mapping in data["data"]:
                            if mapping["attributes"]["externalSite"] == "anilist/manga":
                                send_to = "anilist"
                                send_type = "manga"
                                media_id = mapping["attributes"]["externalId"]
                                source = "anilist"
                                break
                        else:
                            return
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
            case r"(?:https?://)?(?:www\.)?myanimelist\.net/manga/(?P<mediaid>\d+)" as ids:
                send_to = "anilist"
                send_type = "manga"
                media_id = ids["mediaid"]
                source = "myanimelist"
            case r"(?:https?://)?(?:www\.)?notify\.moe/anime/(?P<mediaid>[\w\-_]+)" as ids:
                send_to = "mal"
                send_type = "anime"
                media_id = ids["mediaid"]
                source = "notify"
            case r"(?:https?://)?(?:www\.)?otakotaku\.com/anime/view/(?P<mediaid>[\w\-]+)":
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
                try:
                    async with Simkl() as simkl:
                        smk_dat = await simkl.get_title_ids(ids["mediaid"], "anime")
                        media_id = smk_dat.mal
                        send_to = "mal"
                        send_type = "anime"
                        source = "myanimelist"
                # pylint: disable=broad-exception-caught
                except Exception:
                    return
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
            case _:
                return

        if send_to is None or media_id is None or source is None:
            return

        try:
            match send_to:
                case "anilist":
                    reverse_lookup = source == "myanimelist"
                    async with AniList() as anilist:
                        al_id = await anilist.manga(media_id, from_mal=reverse_lookup)
                        if al_id is None:
                            return
                    await anilist_submit(ctx, al_id)
                case "mal":
                    is_it_source = source == "myanimelist"
                    if is_it_source is False:
                        async with AnimeApi() as aapi:
                            aadat = await aapi.get_relation(media_id, source)
                            media_id = aadat.myanimelist
                            if media_id is None:
                                return
                    await mal_submit(ctx, media_id)
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
