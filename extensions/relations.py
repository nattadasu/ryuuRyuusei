import re
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional

import interactions as ipy

from classes.animeapi import AnimeApi, AnimeApiAnime
from classes.excepts import ProviderHttpError, SimklTypeError
from classes.kitsu import Kitsu
from classes.simkl import Simkl, SimklMediaTypes, SimklRelations
from classes.trakt import Trakt, TraktIdsStruct, TraktMediaStruct
from modules.commons import save_traceback_to_file
from modules.const import EMOJI_UNEXPECTED_ERROR
from modules.platforms import (
    get_platform_color,
    media_id_to_platform,
    platforms_to_fields,
)


@dataclass
class RelationData:
    """Container for all relation data"""

    anime_api: AnimeApiAnime
    simkl_data: SimklRelations
    trakt_data: TraktMediaStruct
    title: str
    simkl_id: Optional[int] = None
    imdb_id: Optional[str] = None
    tmdb_id: Optional[str] = None
    tvdb_id: Optional[str] = None
    trakt_id: Optional[str] = None
    trakt_season: Optional[int] = None
    trakt_type: Optional[str] = None


class RelationsFetcher:
    """Handles fetching relations from various platforms"""

    @staticmethod
    async def get_anime_api(
        media_id: str,
        platform: AnimeApi.AnimeApiPlatforms,
        media_type: Optional[str] = None,
        title_season: Optional[int] = None,
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
        """Fetch SIMKL title IDs"""
        async with Simkl() as simkl:
            return await simkl.get_title_ids(
                media_id=simkl_id, media_type=SimklMediaTypes.ANIME
            )

    @staticmethod
    async def search_simkl(
        provider: Simkl.Provider, media_id: str, media_type=None
    ) -> Optional[int]:
        """Search SIMKL by external ID, returns SIMKL ID or None"""
        try:
            async with Simkl() as simkl:
                entry = await simkl.search_by_id(
                    provider, media_id, media_type=media_type
                )
                if entry:
                    return entry[0]["ids"]["simkl"]
        except (SimklTypeError, ProviderHttpError):
            pass
        return None

    @staticmethod
    async def get_trakt_data(media_id: str, media_type: str) -> TraktMediaStruct:
        """Fetch Trakt data"""
        async with Trakt() as api:
            return await api.get_title_data(
                media_id=media_id, media_type=api.MediaType(media_type)
            )

    @staticmethod
    async def lookup_trakt(
        media_id: str, platform: str, media_type: str
    ) -> Optional[TraktMediaStruct]:
        """Lookup Trakt by external ID"""
        try:
            async with Trakt() as api:
                return await api.lookup(
                    media_id=media_id,
                    platform=api.Platform(platform),
                    media_type=api.MediaType(media_type),
                )
        except ProviderHttpError:
            return None


class PlatformHandler:
    """Handles platform-specific logic for fetching relations"""

    def __init__(self, fetcher: RelationsFetcher):
        self.fetcher = fetcher

    async def handle_anime_platform(
        self, media_id: str, platform: str
    ) -> AnimeApiAnime:
        """Handle standard anime platforms (MAL, AniList, etc.)"""
        platform_map = {
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

        # Handle special cases
        if platform == "shikimori" and not re.match(r"^\d+$", media_id):
            media_id = re.search(r"^\d+", media_id).group(0)
        elif platform == "kitsu" and not re.match(r"^\d+$", media_id):
            async with Kitsu() as api:
                kitsu_data = await api.resolve_slug(
                    slug=media_id, media_type=api.MediaType.ANIME
                )
                media_id = kitsu_data["data"][0]["id"]

        return await self.fetcher.get_anime_api(media_id, platform_map[platform])

    async def handle_simkl(
        self, media_id: str
    ) -> tuple[AnimeApiAnime, SimklRelations, int]:
        """Handle SIMKL platform"""
        simkl_data = await self.fetcher.get_simkl_by_id(int(media_id))
        simkl_id = int(media_id)

        # Try to get AnimeAPI data via SIMKL directly, then MAL as fallback
        anime_api = AnimeApiAnime(title="")
        try:
            anime_api = await self.fetcher.get_anime_api(
                media_id, AnimeApi.AnimeApiPlatforms.SIMKL
            )
        except Exception:
            if simkl_data.mal:
                anime_api = await self.fetcher.get_anime_api(
                    str(simkl_data.mal), AnimeApi.AnimeApiPlatforms.MAL
                )

        return anime_api, simkl_data, simkl_id

    async def handle_external_id(
        self, media_id: str, platform: str, media_type: Optional[str] = None
    ) -> tuple[AnimeApiAnime, SimklRelations, Optional[int]]:
        """Handle external ID platforms (TMDB, TVDB, IMDb)"""
        if platform == "tmdb":
            media_id = media_id.split("/")[0]
            if not media_type:
                raise ValueError("media_type required for TMDB")

        # Map platform names to AnimeAPI platform enum
        platform_map = {
            "tmdb": AnimeApi.AnimeApiPlatforms.THEMOVIEDB,
            "tvdb": AnimeApi.AnimeApiPlatforms.THETVDB,
            "imdb": AnimeApi.AnimeApiPlatforms.IMDB,
        }

        # Try to get AnimeAPI data directly with media_type for TMDB
        anime_api = AnimeApiAnime(title="")
        try:
            if platform == "tmdb":
                anime_api = await self.fetcher.get_anime_api(
                    media_id, platform_map[platform], media_type=media_type
                )
            else:
                anime_api = await self.fetcher.get_anime_api(
                    media_id, platform_map[platform]
                )
        except Exception:
            pass

        # Try to get SIMKL data from AnimeAPI first, then search SIMKL
        simkl_id = None
        simkl_data = SimklRelations()

        if anime_api.simkl:
            simkl_id = anime_api.simkl
            simkl_data = await self.fetcher.get_simkl_by_id(simkl_id)
        else:
            # Search SIMKL as fallback
            simkl_id = await self.fetcher.search_simkl(
                Simkl.Provider(platform), media_id, media_type=media_type
            )

            if not simkl_id:
                raise SimklTypeError(
                    f"Could not find {platform.upper()} ID in SIMKL or AnimeAPI"
                )

            simkl_data = await self.fetcher.get_simkl_by_id(simkl_id)

            # Try to get AnimeAPI data via MAL if not already fetched
            if not anime_api.title and simkl_data.mal:
                anime_api = await self.fetcher.get_anime_api(
                    str(simkl_data.mal), AnimeApi.AnimeApiPlatforms.MAL
                )

        return anime_api, simkl_data, simkl_id

    async def handle_trakt(
        self, media_id: str
    ) -> tuple[AnimeApiAnime, TraktMediaStruct, str, str, int]:
        """Handle Trakt platform, returns (anime_api, trakt_data, trakt_type, trakt_id, trakt_season)"""
        matching = re.match(
            r"^(?P<type>show|movie)s?/(?P<slug>[^/]+)(?:/seasons?/(?P<season>\d+))?$",
            media_id,
        )

        if not matching:
            raise ValueError(
                "Invalid Trakt ID format. Use: <type>/<slug>/[seasons/<season>]"
            )

        trakt_type = matching.group("type")
        trakt_id = matching.group("slug")
        trakt_season = int(matching.group("season") or 1)

        # Get Trakt data
        trakt_data = await self.fetcher.get_trakt_data(trakt_id, f"{trakt_type}s")

        # Get AnimeAPI data
        anime_api = await self.fetcher.get_anime_api(
            f"{trakt_type}/{trakt_id}/seasons/{trakt_season}",
            AnimeApi.AnimeApiPlatforms.TRAKT,
        )

        return anime_api, trakt_data, trakt_type, trakt_id, trakt_season


class RelationsBuilder:
    """Builds complete relation data by combining multiple sources"""

    def __init__(self, fetcher: RelationsFetcher):
        self.fetcher = fetcher

    async def enrich_with_simkl(
        self, anime_api: AnimeApiAnime, simkl_id: Optional[int] = None
    ) -> tuple[SimklRelations, Optional[int]]:
        """Enrich data by searching SIMKL via AnimeAPI, MAL or AniDB"""
        if simkl_id:
            simkl_data = await self.fetcher.get_simkl_by_id(simkl_id)
            return simkl_data, simkl_id

        # First, check if AnimeAPI already has SIMKL ID
        if anime_api.simkl:
            simkl_id = anime_api.simkl
            simkl_data = await self.fetcher.get_simkl_by_id(simkl_id)
            return simkl_data, simkl_id

        # Try to find SIMKL ID via MAL or AniDB
        search_id = anime_api.myanimelist or anime_api.anidb
        if search_id:
            provider = (
                Simkl.Provider.MYANIMELIST
                if anime_api.myanimelist
                else Simkl.Provider.ANIDB
            )
            simkl_id = await self.fetcher.search_simkl(provider, str(search_id))
            if simkl_id:
                simkl_data = await self.fetcher.get_simkl_by_id(simkl_id)
                return simkl_data, simkl_id

        return SimklRelations(), None

    async def enrich_with_trakt(
        self,
        anime_api: AnimeApiAnime,
        simkl_data: SimklRelations,
        trakt_data: Optional[TraktMediaStruct] = None,
    ) -> tuple[Optional[str], Optional[str], Optional[int]]:
        """Enrich data with Trakt information"""
        # If already have Trakt data from anime_api
        if anime_api.trakt:
            # Convert enum to string value if needed
            trakt_type = (
                anime_api.trakt_type.value
                if hasattr(anime_api.trakt_type, "value")
                else str(anime_api.trakt_type)
            )
            trakt_season = anime_api.trakt_season
            trakt_id = f"{trakt_type}/{anime_api.trakt}/seasons/{trakt_season}"
            return trakt_id, trakt_type, trakt_season

        # Try to lookup Trakt via IMDb or TMDB from AnimeAPI first
        imdb_id = anime_api.imdb or simkl_data.imdb
        tmdb_id = anime_api.themoviedb or simkl_data.tmdb

        if imdb_id or tmdb_id:
            lookup_id = imdb_id or tmdb_id
            lookup_platform = "imdb" if imdb_id else "tmdb"

            # Determine media type from AnimeAPI or SIMKL
            if anime_api.themoviedb_type:
                # Convert enum to string value if needed
                tmdb_type_str = (
                    anime_api.themoviedb_type.value
                    if hasattr(anime_api.themoviedb_type, "value")
                    else str(anime_api.themoviedb_type)
                )
                media_type = "movies" if tmdb_type_str == "movie" else "shows"
            elif simkl_data.anitype == "movie" or simkl_data.type == "movie":
                media_type = "movies"
            else:
                media_type = "shows"

            trakt_lookup = await self.fetcher.lookup_trakt(
                lookup_id, lookup_platform, media_type
            )

            if trakt_lookup:
                trakt_type = trakt_lookup.type
                trakt_obj = (
                    trakt_lookup.show if trakt_type == "show" else trakt_lookup.movie
                )
                trakt_id = f"{trakt_type}/{trakt_obj.ids.trakt}"
                return trakt_id, trakt_type, 1

        return None, None, None

    def build_media_type_info(
        self,
        anime_api: AnimeApiAnime,
        simkl_data: SimklRelations,
        trakt_type: Optional[str] = None,
    ) -> tuple[str, str]:
        """Determine TVDB and TMDB media type strings"""
        # Try AnimeAPI data first
        if anime_api.themoviedb_type:
            # Convert enum to string value if needed
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
        elif trakt_type:
            tvtyp = "series" if trakt_type == "show" else "movies"
            tmtyp = "tv" if trakt_type == "show" else "movie"
        else:
            tvtyp = "series"
            tmtyp = "tv"

        return tvtyp, tmtyp

    def build_external_urls(
        self,
        anime_api: AnimeApiAnime,
        simkl_data: SimklRelations,
        trakt_data: TraktMediaStruct,
        trakt_season: Optional[int],
        tvtyp: str,
        tmtyp: str,
        tmdb_id: Optional[str] = None,
    ) -> tuple[Optional[str], Optional[str], Optional[str]]:
        """Build TVDB, TVTime, and TMDB URLs"""
        # TVDB URL - use AnimeAPI data first, then SIMKL, then Trakt
        tvdb_id = None
        tvdb_raw = (
            anime_api.thetvdb
            or simkl_data.tvdb
            or (trakt_data.ids.tvdb if trakt_data.ids else None)
        )

        if trakt_season:
            if simkl_data.tvdbslug:
                tvdb_id = f"https://www.thetvdb.com/{tvtyp}/{simkl_data.tvdbslug}/seasons/official/{trakt_season}"
            elif tvdb_raw:
                tvdb_id = f"https://www.thetvdb.com/deferrer/{tvtyp}/{tvdb_raw}"
        else:
            if simkl_data.tvdbslug:
                tvdb_id = f"https://www.thetvdb.com/{tvtyp}/{simkl_data.tvdbslug}"
            elif tvdb_raw:
                tvdb_id = f"https://www.thetvdb.com/deferrer/{tvtyp}/{tvdb_raw}"

        # TVTime ID - use AnimeAPI data first, then SIMKL, then Trakt
        tvtime_id = None
        if tvdb_raw:
            tvtime_id = f"{'show' if tvtyp == 'series' else 'movie'}/{tvdb_raw}"

        # TMDB URL
        tmdb_url = None
        if tmdb_id:
            if trakt_season:
                tmdb_url = f"{tmtyp}/{tmdb_id}/season/{trakt_season}"
            else:
                tmdb_url = f"{tmtyp}/{tmdb_id}"

        return tvdb_id, tvtime_id, tmdb_url


class ExternalSitesRelations(ipy.Extension):
    """Extension class for /relations"""

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
        self.builder = RelationsBuilder(self.fetcher)

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
                    ipy.SlashCommandChoice(
                        name="Trakt (requires <type>/<slug>/seasons/<season>)",
                        value="trakt",
                    ),
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
            "trakt",
        ],
        media_type: Literal["show", "movie"] | None = None,
    ) -> None:
        """Main handler for relations command"""
        try:
            # Step 1: Fetch initial data based on platform
            (
                anime_api,
                simkl_data,
                simkl_id,
                trakt_data,
                trakt_info,
            ) = await self._fetch_initial_data(ctx, media_id, platform, media_type)

            if not anime_api:  # Error already sent to user
                return

            # Step 2: Enrich with additional data
            await self._enrich_data(
                anime_api, simkl_data, simkl_id, trakt_data, trakt_info, platform
            )

            # Step 3: Build and send embed
            await self._build_and_send_embed(
                ctx,
                platform,
                media_id,
                anime_api,
                simkl_data,
                simkl_id,
                trakt_data,
                trakt_info,
            )

        except Exception as e:
            await ctx.send(f"❌ An unexpected error occurred: {str(e)}")
            save_traceback_to_file("relations_show", ctx.author, e)

    async def _fetch_initial_data(
        self, ctx, media_id: str, platform: str, media_type: Optional[str]
    ) -> tuple:
        """Fetch initial data from the specified platform"""
        anime_api = AnimeApiAnime(title="")
        simkl_data = SimklRelations()
        simkl_id = None
        trakt_data = TraktMediaStruct("", 0, TraktIdsStruct(0, ""))
        trakt_info = {"type": None, "id": None, "season": None}

        try:
            if platform == "simkl":
                anime_api, simkl_data, simkl_id = await self.handler.handle_simkl(
                    media_id
                )

            elif platform in ["tmdb", "tvdb", "imdb"]:
                anime_api, simkl_data, simkl_id = await self.handler.handle_external_id(
                    media_id, platform, media_type
                )

            elif platform == "trakt":
                (
                    anime_api,
                    trakt_data,
                    trakt_type,
                    trakt_id,
                    trakt_season,
                ) = await self.handler.handle_trakt(media_id)
                trakt_info = {
                    "type": trakt_type,
                    "id": trakt_id,
                    "season": trakt_season,
                }

            else:  # Standard anime platforms
                anime_api = await self.handler.handle_anime_platform(media_id, platform)

            return anime_api, simkl_data, simkl_id, trakt_data, trakt_info

        except ValueError as e:
            await ctx.send(f"❌ {str(e)}")
            return None, None, None, None, None
        except SimklTypeError as e:
            await ctx.send(f"❌ Could not find the title in SIMKL: {str(e)}")
            save_traceback_to_file("relations_show", ctx.author, e)
            return None, None, None, None, None
        except ProviderHttpError as e:
            await ctx.send(f"❌ API error: {str(e)}")
            save_traceback_to_file("relations_show", ctx.author, e)
            return None, None, None, None, None

    async def _enrich_data(
        self, anime_api, simkl_data, simkl_id, trakt_data, trakt_info, platform
    ):
        """Enrich data with additional information from other sources"""
        # Enrich with SIMKL if not already present
        if not simkl_id and platform not in ["simkl", "trakt", "tmdb", "tvdb", "imdb"]:
            simkl_data, simkl_id = await self.builder.enrich_with_simkl(
                anime_api, simkl_id
            )

        # Enrich with Trakt if not already present
        if not trakt_info["id"] and platform != "trakt":
            trakt_id, trakt_type, trakt_season = await self.builder.enrich_with_trakt(
                anime_api, simkl_data, trakt_data
            )
            if trakt_id:
                trakt_info = {
                    "type": trakt_type,
                    "id": trakt_id,
                    "season": trakt_season,
                }

        # For Trakt platform, also fetch SIMKL data
        if platform == "trakt" and not simkl_id:
            # First check if AnimeAPI has SIMKL ID
            if anime_api.simkl:
                simkl_id = anime_api.simkl
                simkl_data = await self.fetcher.get_simkl_by_id(simkl_id)
            else:
                # Try to find SIMKL via MAL, IMDb, TMDB, or TVDB
                search_sources = [
                    (anime_api.myanimelist, Simkl.Provider.MYANIMELIST, None),
                    (trakt_data.ids.imdb, Simkl.Provider.IMDB, None),
                    (
                        trakt_data.ids.tmdb,
                        Simkl.Provider.TMDB,
                        Simkl.TmdbMediaTypes.MOVIE
                        if trakt_info["type"] == "movie"
                        else Simkl.TmdbMediaTypes.TV,
                    ),
                    (trakt_data.ids.tvdb, Simkl.Provider.TVDB, None),
                ]

                for source_id, provider, media_type in search_sources:
                    if source_id:
                        simkl_id = await self.fetcher.search_simkl(
                            provider, str(source_id), media_type
                        )
                        if simkl_id:
                            simkl_data = await self.fetcher.get_simkl_by_id(simkl_id)
                            break

    async def _build_and_send_embed(
        self,
        ctx,
        platform,
        media_id,
        anime_api,
        simkl_data,
        simkl_id,
        trakt_data,
        trakt_info,
    ):
        """Build and send the relations embed"""
        # Determine title
        title = anime_api.title or simkl_data.title or "Unknown"

        # Build media type info
        tvtyp, tmtyp = self.builder.build_media_type_info(
            anime_api, simkl_data, trakt_info["type"]
        )

        # Build external URLs - use AnimeAPI data first, then SIMKL as fallback
        if platform == "tmdb":
            tmdb_id = media_id
        else:
            tmdb_id = anime_api.themoviedb or simkl_data.tmdb

        if platform == "imdb":
            imdb_id = media_id
        else:
            imdb_id = anime_api.imdb or simkl_data.imdb

        tvdb_id, tvtime_id, tmdb_url = self.builder.build_external_urls(
            anime_api,
            simkl_data,
            trakt_data,
            trakt_info["season"],
            tvtyp,
            tmtyp,
            tmdb_id,
        )

        # Build trakt_id string - use AnimeAPI data first
        if trakt_info["id"]:
            trakt_id_str = trakt_info["id"]
        elif anime_api.trakt:
            # Build full Trakt URL with type and season from AnimeAPI
            trakt_type_str = (
                anime_api.trakt_type.value
                if hasattr(anime_api.trakt_type, "value")
                else str(anime_api.trakt_type)
            )

            # Only add season for shows, not movies
            if trakt_type_str == "shows":
                trakt_season = anime_api.trakt_season or 1
                trakt_id_str = (
                    f"{trakt_type_str}/{anime_api.trakt}/seasons/{trakt_season}"
                )
            else:
                trakt_id_str = f"{trakt_type_str}/{anime_api.trakt}"
        else:
            trakt_id_str = None

        # Build letterboxd link: use slug if available, otherwise use TMDB redirect
        letterboxd_link = None
        if anime_api.letterboxd_slug:
            letterboxd_link = anime_api.letterboxd_slug
        elif tmdb_id and tmtyp == "movie":
            letterboxd_link = f"tmdb/{tmdb_id}"

        # Generate fields
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
            simkl=simkl_id or anime_api.simkl,
            simkl_type=simkl_data.type,
            trakt=trakt_id_str,
            tvdb=tvdb_id,
            tvtime=tvtime_id,
            tmdb=tmdb_url,
            tvtyp=tvtyp,
        )

        # Fix media_id for display
        if platform == "tvdb":
            if re.match(r"^\d+$", media_id):
                media_id = f"https://www.thetvdb.com/deferrer/{tvtyp}/{media_id}"
            else:
                media_id = f"https://www.thetvdb.com/{tvtyp}/{media_id}"
        elif platform == "trakt":
            media_id = f"{trakt_info['type']}/{trakt_info['id']}"
        elif platform == "tmdb":
            media_id = f"{tmtyp}/{media_id}"

        # Get platform info
        pfs = media_id_to_platform(
            media_id=media_id, platform=platform, simkl_type=simkl_data.type
        )

        # Determine poster
        poster = None
        poster_src = None
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

        # Build embed
        if fields:
            embed = ipy.Embed(
                author=ipy.EmbedAuthor(
                    name=f"Looking external site relations from {pfs.pf}",
                    icon_url=f"https://cdn.discordapp.com/emojis/{pfs.emoid}.png?v=1",
                    url="/".join(pfs.uid.split("/")[:3]),
                ),
                title=title,
                url=pfs.uid,
                description="Data might be inaccurate, especially for sequels of the title (as IMDb, TVDB, TMDB, and Trakt rely on per title entry rather than season entry)",
                color=get_platform_color(platform),
                fields=fields,
                footer=ipy.EmbedFooter(
                    text=f"Powered by nattadasu's AnimeAPI, Trakt, and SIMKL.{poster_text}"
                ),
            )
            embed.set_thumbnail(url=poster)
        else:
            embed = ipy.Embed(
                title="Whoops!",
                description=f"No relations found on {pfs.pf} with the following URL: <{pfs.uid}>!\nEither the anime is not in the database, or you have entered the wrong ID.",
                color=0xFF0000,
                timestamp=datetime.utcnow(),
            )
            emoji_error = re.search(r"\<(a?)\:(\w+)\:(\d+)\>", EMOJI_UNEXPECTED_ERROR)
            if emoji_error:
                embed.set_thumbnail(
                    url=f"https://cdn.discordapp.com/emojis/{emoji_error.group(2)}.png?v=1"
                )

        await ctx.send(embed=embed)


def setup(bot: ipy.AutoShardedClient) -> None:
    ExternalSitesRelations(bot)
