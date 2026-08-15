import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

import interactions as ipy

from classes.animeapi import AnimeApi, AnimeApiAnime
from classes.excepts import ProviderHttpError, SimklTypeError
from classes.kitsu import Kitsu
from classes.simkl import Simkl, SimklMediaTypes, SimklRelations
from modules.commons import save_traceback_to_file
from modules.const import EMOJI_UNEXPECTED_ERROR
from modules.platforms import (
    get_platform_color,
    media_id_to_platform,
    platforms_to_fields,
)

ANIME_PLATFORM_MAP: dict[str, AnimeApi.AnimeApiPlatforms] = {
    "myanimelist": AnimeApi.AnimeApiPlatforms.MYANIMELIST,
    "anilist": AnimeApi.AnimeApiPlatforms.ANILIST,
    "anidb": AnimeApi.AnimeApiPlatforms.ANIDB,
    "kitsu": AnimeApi.AnimeApiPlatforms.KITSU,
    "animeplanet": AnimeApi.AnimeApiPlatforms.ANIMEPLANET,
    "animenewsnetwork": AnimeApi.AnimeApiPlatforms.ANIMENEWSNETWORK,
    "anisearch": AnimeApi.AnimeApiPlatforms.ANISEARCH,
    "annict": AnimeApi.AnimeApiPlatforms.ANNICT,
    "kaize": AnimeApi.AnimeApiPlatforms.KAIZE,
    "livechart": AnimeApi.AnimeApiPlatforms.LIVECHART,
    "nautiljon": AnimeApi.AnimeApiPlatforms.NAUTILJON,
    "notify": AnimeApi.AnimeApiPlatforms.NOTIFYMOE,
    "otakotaku": AnimeApi.AnimeApiPlatforms.OTAKOTAKU,
    "shikimori": AnimeApi.AnimeApiPlatforms.SHIKIMORI,
    "shoboi": AnimeApi.AnimeApiPlatforms.SHOBOI,
    "silveryasha": AnimeApi.AnimeApiPlatforms.SILVERYASHA,
}

EXTERNAL_PLATFORM_MAP: dict[str, AnimeApi.AnimeApiPlatforms] = {
    "tmdb": AnimeApi.AnimeApiPlatforms.THEMOVIEDB,
    "tvdb": AnimeApi.AnimeApiPlatforms.THETVDB,
    "imdb": AnimeApi.AnimeApiPlatforms.IMDB,
}


@dataclass
class ResolvedRelationState:
    """Unified container storing resolution output across platforms"""

    anime_api: AnimeApiAnime = field(default_factory=lambda: AnimeApiAnime(title=""))
    simkl_data: SimklRelations = field(default_factory=SimklRelations)
    simkl_id: int | None = None


class RelationsFetcher:
    """Low-level API interaction helper"""

    @staticmethod
    async def get_anime_api(
        media_id: str,
        platform: AnimeApi.AnimeApiPlatforms,
        media_type: str | None = None,
        title_season: int | None = None,
    ) -> AnimeApiAnime:
        """Fetch AnimeAPI relation data"""
        async with AnimeApi() as api:
            return await api.get_relation(
                media_id=media_id,
                platform=platform,
                media_type=media_type,
                title_season=title_season,
            )

    @staticmethod
    async def get_simkl_by_id(simkl_id: int) -> SimklRelations:
        """Fetch SIMKL title relations"""
        async with Simkl() as simkl:
            return await simkl.get_title_ids(
                media_id=simkl_id, media_type=SimklMediaTypes.ANIME
            )

    @staticmethod
    async def search_simkl(
        provider: Simkl.Provider | str, media_id: str, media_type: str | None = None
    ) -> int | None:
        """Resolve SIMKL ID via search/redirect endpoint"""
        try:
            async with Simkl() as simkl:
                entry = await simkl.search_by_id(
                    provider, media_id, media_type=media_type
                )
                if entry and isinstance(entry, list) and len(entry) > 0:
                    return entry[0].get("ids", {}).get("simkl")
        except (SimklTypeError, ProviderHttpError):
            pass
        return None


class PlatformHandler:
    """Platform-specific resolution logic"""

    def __init__(self, fetcher: RelationsFetcher):
        self.fetcher = fetcher

    async def handle_anime_platform(
        self, media_id: str, platform: str
    ) -> AnimeApiAnime:
        """Resolve standard anime platforms"""
        if platform == "shikimori" and not re.match(r"^\d+$", media_id):
            match = re.search(r"^\d+", media_id)
            if match:
                media_id = match.group(0)

        elif platform == "kitsu" and not re.match(r"^\d+$", media_id):
            async with Kitsu() as api:
                kitsu_data = await api.resolve_slug(
                    slug=media_id, media_type=api.MediaType.ANIME
                )
                if kitsu_data.get("data"):
                    media_id = kitsu_data["data"][0]["id"]

        return await self.fetcher.get_anime_api(media_id, ANIME_PLATFORM_MAP[platform])

    async def handle_simkl(
        self, media_id: str
    ) -> tuple[AnimeApiAnime, SimklRelations, int]:
        """Resolve SIMKL platform input"""
        simkl_id = int(media_id)
        simkl_data = await self.fetcher.get_simkl_by_id(simkl_id)
        anime_api = AnimeApiAnime(title="")

        try:
            anime_api = await self.fetcher.get_anime_api(
                media_id, AnimeApi.AnimeApiPlatforms.SIMKL
            )
        except Exception:  # noqa: BLE001
            if simkl_data.mal:
                anime_api = await self.fetcher.get_anime_api(
                    str(simkl_data.mal), AnimeApi.AnimeApiPlatforms.MAL
                )

        return anime_api, simkl_data, simkl_id

    async def handle_external_id(
        self, media_id: str, platform: str, media_type: str | None = None
    ) -> tuple[AnimeApiAnime, SimklRelations, int | None]:
        """Resolve TMDB, TVDB, IMDb external ID inputs"""
        if platform == "tmdb":
            media_id = media_id.split("/")[0]
            if not media_type:
                raise ValueError("media_type option is required for TMDB")

        anime_api = AnimeApiAnime(title="")
        try:
            anime_api = await self.fetcher.get_anime_api(
                media_id, EXTERNAL_PLATFORM_MAP[platform], media_type=media_type
            )
        except Exception as e:  # noqa: BLE001
            save_traceback_to_file("relations", None, e, mute_error=True)

        simkl_id = None
        simkl_data = SimklRelations()

        if anime_api.simkl:
            simkl_id = anime_api.simkl
            simkl_data = await self.fetcher.get_simkl_by_id(simkl_id)
        else:
            simkl_id = await self.fetcher.search_simkl(
                Simkl.Provider(platform), media_id, media_type=media_type
            )
            if not simkl_id:
                raise SimklTypeError(
                    f"Could not find {platform.upper()} ID on SIMKL or AnimeAPI"
                )

            simkl_data = await self.fetcher.get_simkl_by_id(simkl_id)

            if not anime_api.title and simkl_data.mal:
                anime_api = await self.fetcher.get_anime_api(
                    str(simkl_data.mal), AnimeApi.AnimeApiPlatforms.MAL
                )

        return anime_api, simkl_data, simkl_id


class RelationsEnricher:
    """Cross-platform enrichment pipeline"""

    def __init__(self, fetcher: RelationsFetcher):
        self.fetcher = fetcher

    async def enrich_simkl(self, state: ResolvedRelationState, platform: str) -> None:
        """Cross-reference SIMKL database"""
        if state.simkl_id or platform in ("simkl", "tmdb", "tvdb", "imdb"):
            return

        if state.anime_api.simkl:
            state.simkl_id = state.anime_api.simkl
            state.simkl_data = await self.fetcher.get_simkl_by_id(state.simkl_id)
            return

        search_id = state.anime_api.myanimelist or state.anime_api.anidb
        if search_id:
            provider = (
                Simkl.Provider.MYANIMELIST
                if state.anime_api.myanimelist
                else Simkl.Provider.ANIDB
            )
            simkl_id = await self.fetcher.search_simkl(provider, str(search_id))
            if simkl_id:
                state.simkl_id = simkl_id
                state.simkl_data = await self.fetcher.get_simkl_by_id(simkl_id)


class RelationsViewBuilder:
    """Builds interactive Discord Embed visual representations"""

    @staticmethod
    def derive_media_types(
        anime_api: AnimeApiAnime,
        simkl_data: SimklRelations,
    ) -> tuple[str, str]:
        """Derive (tv_type, tmdb_type) string identifiers"""
        if anime_api.themoviedb_type:
            tmtyp = (
                anime_api.themoviedb_type.value
                if hasattr(anime_api.themoviedb_type, "value")
                else str(anime_api.themoviedb_type)
            )
            tvtyp = "series" if tmtyp == "tv" else "movies"
        elif simkl_data.anitype:
            tvtyp = "series" if simkl_data.anitype == "tv" else "movies"
            tmtyp = "tv" if simkl_data.anitype == "tv" else "movie"
        elif simkl_data.type:
            tvtyp = "series" if simkl_data.type == "show" else "movies"
            tmtyp = "tv" if simkl_data.type == "show" else "movie"
        else:
            tvtyp, tmtyp = "series", "tv"

        return tvtyp, tmtyp

    @classmethod
    def build_embed(
        cls,
        platform: str,
        raw_media_id: str,
        state: ResolvedRelationState,
    ) -> ipy.Embed:
        """Construct the complete relations Embed component"""
        anime_api = state.anime_api
        simkl_data = state.simkl_data

        title = anime_api.title or simkl_data.title or "Unknown"
        tvtyp, tmtyp = cls.derive_media_types(anime_api, simkl_data)

        tmdb_id = (
            raw_media_id
            if platform == "tmdb"
            else (anime_api.themoviedb or simkl_data.tmdb)
        )
        imdb_id = (
            raw_media_id if platform == "imdb" else (anime_api.imdb or simkl_data.imdb)
        )

        tvdb_raw = anime_api.thetvdb or simkl_data.tvdb

        # Build TVDB URL
        tvdb_url = None
        if simkl_data.tvdbslug:
            tvdb_url = f"https://www.thetvdb.com/{tvtyp}/{simkl_data.tvdbslug}"
        elif tvdb_raw:
            tvdb_url = f"https://www.thetvdb.com/deferrer/{tvtyp}/{tvdb_raw}"

        # TVTime
        tvtime_url = (
            f"{'show' if tvtyp == 'series' else 'movie'}/{tvdb_raw}"
            if tvdb_raw
            else None
        )

        # TMDB
        tmdb_url = f"{tmtyp}/{tmdb_id}" if tmdb_id else None

        # Trakt String
        if anime_api.trakt:
            if hasattr(anime_api.trakt_type, "value"):
                t_type = anime_api.trakt_type.value
            elif anime_api.trakt_type:
                t_type = str(anime_api.trakt_type)
            else:
                t_type = "shows" if simkl_data.type in ("show", "tv") else "movies"
            trakt_str = f"{t_type}/{anime_api.trakt}"
        elif simkl_data.trakt:
            t_type = "shows" if simkl_data.type in ("show", "tv") else "movies"
            trakt_str = f"{t_type}/{simkl_data.trakt}"
        else:
            trakt_str = None

        # Letterboxd
        letterboxd_link = None
        if anime_api.letterboxd_slug:
            letterboxd_link = f"film/{anime_api.letterboxd_slug}"
        elif simkl_data.letterboxd:
            letterboxd_link = f"film/{simkl_data.letterboxd}"
        elif tmtyp == "movie":
            if tmdb_id:
                letterboxd_link = f"tmdb/{tmdb_id}"
            elif imdb_id:
                letterboxd_link = f"imdb/{imdb_id}"

        fields = platforms_to_fields(
            currPlatform=platform,
            allcin=simkl_data.allcin,
            anidb=anime_api.anidb,
            anilist=anime_api.anilist,
            ann=anime_api.animenewsnetwork or simkl_data.ann,
            animeplanet=anime_api.animeplanet,
            anisearch=anime_api.anisearch,
            annict=anime_api.annict,
            imdb=imdb_id,
            kaize=anime_api.kaize,
            kitsu=anime_api.kitsu,
            letterboxd=letterboxd_link,
            livechart=anime_api.livechart,
            myanimelist=anime_api.myanimelist,
            nautiljon=anime_api.nautiljon,
            notify=anime_api.notify,
            otakotaku=anime_api.otakotaku,
            shikimori=anime_api.shikimori,
            shoboi=anime_api.shoboi,
            silveryasha=anime_api.silveryasha,
            simkl=state.simkl_id or anime_api.simkl,
            simkl_type=simkl_data.type,
            trakt=trakt_str,
            tvdb=tvdb_url,
            tvtime=tvtime_url,
            tmdb=tmdb_url,
            tvtyp=tvtyp,
        )

        display_media_id = raw_media_id
        if platform == "tvdb":
            display_media_id = (
                f"https://www.thetvdb.com/deferrer/{tvtyp}/{raw_media_id}"
                if re.match(r"^\d+$", raw_media_id)
                else f"https://www.thetvdb.com/{tvtyp}/{raw_media_id}"
            )
        elif platform == "tmdb":
            display_media_id = f"{tmtyp}/{raw_media_id}"

        pfs = media_id_to_platform(
            media_id=display_media_id, platform=platform, simkl_type=simkl_data.type
        )

        if not fields:
            embed = ipy.Embed(
                title="Whoops!",
                description=(
                    f"No relations found on {pfs.pf} with the following URL: <{pfs.uid}>!\n"
                    "Either the title is missing from the database, or the ID was incorrect."
                ),
                color=0xFF0000,
                timestamp=datetime.now(timezone.utc),
            )
            emoji_match = re.search(r"\<(a?)\:(\w+)\:(\d+)\>", EMOJI_UNEXPECTED_ERROR)
            if emoji_match:
                embed.set_thumbnail(
                    url=f"https://cdn.discordapp.com/emojis/{emoji_match.group(2)}.png?v=1"
                )
            return embed

        poster, poster_src = None, None
        if simkl_data.poster:
            poster = f"https://simkl.in/posters/{simkl_data.poster}_m.webp"
            poster_src = "SIMKL"
        elif anime_api.notify:
            poster = (
                f"https://media.notify.moe/images/anime/original/{anime_api.notify}.jpg"
            )
            poster_src = "Notify.moe"
        elif anime_api.kitsu:
            poster = f"https://media.kitsu.app/anime/poster_images/{anime_api.kitsu}/large.jpg"
            poster_src = "Kitsu"

        poster_text = f" Poster from {poster_src}" if poster_src else ""

        embed = ipy.Embed(
            author=ipy.EmbedAuthor(
                name=f"Looking external site relations from {pfs.pf}",
                icon_url=f"https://cdn.discordapp.com/emojis/{pfs.emoid}.png?v=1",
                url="/".join(pfs.uid.split("/")[:3]),
            ),
            title=title,
            url=pfs.uid,
            description=(
                "Data might be inaccurate, especially for sequels of the title "
                "(as IMDb, TVDB, and TMDB rely on per-title entries rather than season entries)"
            ),
            color=get_platform_color(platform),
            fields=fields,
            footer=ipy.EmbedFooter(
                text=f"Powered by nattadasu's AnimeAPI and SIMKL.{poster_text}"
            ),
        )
        if poster:
            embed.set_thumbnail(url=poster)
        return embed


class ExternalSitesRelations(ipy.Extension):
    """Extension command handler for /relations"""

    relations = ipy.SlashCommand(
        name="relations",
        description="Get external links relations of a title from one of the supported sites",
        cooldown=ipy.Cooldown(
            cooldown_bucket=ipy.Buckets.CHANNEL,
            rate=1,
            interval=30,
        ),
    )

    def __init__(self, bot: ipy.AutoShardedClient):
        self.bot = bot
        self.fetcher = RelationsFetcher()
        self.handler = PlatformHandler(self.fetcher)
        self.enricher = RelationsEnricher(self.fetcher)

    @relations.subcommand(
        sub_cmd_name="shows",
        sub_cmd_description="Get external links relations of a show from one of the supported sites",
        options=[
            ipy.SlashCommandOption(
                name="media_id",
                description="The media ID of the show",
                type=ipy.OptionType.STRING,
                required=True,
            ),
            ipy.SlashCommandOption(
                name="platform",
                description="The platform to get the relations from",
                type=ipy.OptionType.STRING,
                choices=[
                    ipy.SlashCommandChoice(name="aniDB", value="anidb"),
                    ipy.SlashCommandChoice(name="AniList", value="anilist"),
                    ipy.SlashCommandChoice(name="ANN", value="animenewsnetwork"),
                    ipy.SlashCommandChoice(name="Anime-Planet", value="animeplanet"),
                    ipy.SlashCommandChoice(name="aniSearch", value="anisearch"),
                    ipy.SlashCommandChoice(name="Annict", value="annict"),
                    ipy.SlashCommandChoice(name="IMDb", value="imdb"),
                    ipy.SlashCommandChoice(name="Kaize", value="kaize"),
                    ipy.SlashCommandChoice(name="Kitsu", value="kitsu"),
                    ipy.SlashCommandChoice(name="LiveChart", value="livechart"),
                    ipy.SlashCommandChoice(name="MyAnimeList", value="myanimelist"),
                    ipy.SlashCommandChoice(name="Nautiljon", value="nautiljon"),
                    ipy.SlashCommandChoice(name="Notify.moe", value="notify"),
                    ipy.SlashCommandChoice(name="Otak Otaku", value="otakotaku"),
                    ipy.SlashCommandChoice(name="Shikimori", value="shikimori"),
                    ipy.SlashCommandChoice(name="Shoboi", value="shoboi"),
                    ipy.SlashCommandChoice(
                        name="Silver Yasha: DB Tontonan Indonesia", value="silveryasha"
                    ),
                    ipy.SlashCommandChoice(name="SIMKL", value="simkl"),
                    ipy.SlashCommandChoice(name="The Movie Database", value="tmdb"),
                    ipy.SlashCommandChoice(name="The TVDB", value="tvdb"),
                ],
                required=True,
            ),
            ipy.SlashCommandOption(
                name="media_type",
                description="The media type of the show, required for TMDB",
                type=ipy.OptionType.STRING,
                choices=[
                    ipy.SlashCommandChoice(name="TV Shows", value="show"),
                    ipy.SlashCommandChoice(name="Movie", value="movie"),
                ],
                required=False,
            ),
        ],
    )
    async def relations_shows(
        self,
        ctx: ipy.SlashContext,
        media_id: str,
        platform: Literal[
            "anidb",
            "anilist",
            "animenewsnetwork",
            "animeplanet",
            "anisearch",
            "annict",
            "imdb",
            "kaize",
            "kitsu",
            "livechart",
            "myanimelist",
            "nautiljon",
            "notify",
            "otakotaku",
            "shikimori",
            "shoboi",
            "silveryasha",
            "simkl",
            "tmdb",
            "tvdb",
        ],
        media_type: Literal["show", "movie"] | None = None,
    ) -> None:
        """Main handler for relations command"""
        state = ResolvedRelationState()

        try:
            if platform == "simkl":
                (
                    state.anime_api,
                    state.simkl_data,
                    state.simkl_id,
                ) = await self.handler.handle_simkl(media_id)

            elif platform in ("tmdb", "tvdb", "imdb"):
                (
                    state.anime_api,
                    state.simkl_data,
                    state.simkl_id,
                ) = await self.handler.handle_external_id(
                    media_id, platform, media_type
                )

            else:
                state.anime_api = await self.handler.handle_anime_platform(
                    media_id, platform
                )

            # Cross-enrich state with SIMKL data
            await self.enricher.enrich_simkl(state, platform)

            # Render Embed
            embed = RelationsViewBuilder.build_embed(platform, media_id, state)
            await ctx.send(embed=embed)

        except ValueError as e:
            await ctx.send(f"❌ {e!s}")
        except SimklTypeError as e:
            await ctx.send(f"❌ Could not find the title in SIMKL: {e!s}")
            save_traceback_to_file("relations_show", ctx.author, e)
        except ProviderHttpError as e:
            await ctx.send(f"❌ API error: {e!s}")
            save_traceback_to_file("relations_show", ctx.author, e)
        except Exception as e:  # noqa: BLE001
            await ctx.send(f"❌ An unexpected error occurred: {e!s}")
            save_traceback_to_file("relations_show", ctx.author, e)


def setup(bot: ipy.AutoShardedClient) -> None:
    ExternalSitesRelations(bot)
