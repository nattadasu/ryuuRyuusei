import json
from dataclasses import asdict, dataclass
from datetime import datetime as dt
from enum import Enum
from typing import Literal

from aiohttp import ClientSession

from classes.cache import Caching
from modules.const import USER_AGENT

Cache = Caching(cache_directory="cache/animeapi", cache_expiration_time=86400)


@dataclass
class AnimeApiAnime:
    """AnimeAPI Anime Dataclass"""

    title: str | None = None
    """Title of the anime"""
    anidb: int | None = None
    """AniDB ID"""
    anilist: int | None = None
    """AniList ID"""
    animeplanet: str | None = None
    """Anime-Planet slug"""
    anisearch: int | None = None
    """AniSearch ID"""
    annict: int | None = None
    """Annict ID"""
    kaize: str | None = None
    """Kaize slug"""
    kitsu: int | None = None
    """Kitsu ID, user must resolve slug to ID if using this"""
    livechart: int | None = None
    """LiveChart ID"""
    myanimelist: int | None = None
    """MyAnimeList ID"""
    notify: str | None = None
    """Notify.moe Base64 ID"""
    otakotaku: int | None = None
    """Otak Otaku ID"""
    shikimori: int | None = None
    """Shikimori ID, basically prefixless MyAnimeList ID"""
    shoboi: int | None = None
    """Shoboi ID"""
    silveryasha: int | None = None
    """SilverYasha Database Tontonan Indonesia ID"""
    trakt: int | None = None
    """Trakt ID, user must resolve slug to ID if using this"""
    trakt_type: Literal["shows", "movies"] | None = None
    """Trakt type, either shows or movies, or None if not available"""
    trakt_season: int | None = None
    """Trakt season number, or None if not available"""

    def to_dict(self):
        """Converts the AnimeAPI object to a dictionary, if needed"""
        return asdict(self)


class AnimeApi:
    """AnimeAPI API Wrapper"""

    def __init__(self):
        """Initialize the AniAPI API Wrapper"""
        self.base_url = "https://aniapi.nattadasu.my.id"
        self.session = None

    async def __aenter__(self):
        """Create the session with aiohttp"""
        self.session = ClientSession(headers={"User-Agent": USER_AGENT})
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Close the session"""
        await self.session.close()

    async def close(self) -> None:
        """Close the session"""
        await self.session.close()

    class AnimeApiPlatforms(Enum):
        """Anime API supported platforms enum"""

        ANI_SEARCH = ANISEARCH = AS = "anisearch"
        ANIDB = "anidb"
        ANILIST = AL = "anilist"
        ANIME_PLANET = ANIMEPLANET = AP = "animeplanet"
        ANNICT = "annict"
        KAIZE = "kaize"
        KITSU = "kitsu"
        LIVECHART = LC = "livechart"
        MYANIMELIST = MAL = "myanimelist"
        NOTIFY = "notify"
        OTAKOTAKU = "otakotaku"
        SHIKIMORI = SHIKI = "shikimori"
        SHOBOI = SYOBOI = "shoboi"
        SILVERYASHA = "silveryasha"
        TRAKT = "trakt"

    async def get_update_time(self) -> dt:
        """
        Get the last update time of AniAPI's database

        Returns:
            datetime: The last update time of AniAPI's database
        """
        cache_file_path = Cache.get_cache_file_path("updated")
        cached_data = Cache.read_cached_data(cache_file_path)
        if cached_data is not None:
            cached_data = dt.fromtimestamp(cached_data["timestamp"])
            return cached_data
        try:
            async with self.session.get(f"{self.base_url}/updated") as resp:
                text = await resp.text()
                # format: Updated on %m/%d/%Y %H:%M:%S UTC
                text = text.replace("Updated on ", "")
                text = text.replace(" UTC", "+00:00")
                final = dt.strptime(text, "%m/%d/%Y %H:%M:%S%z").timestamp()
                Cache.write_data_to_cache(
                    {"timestamp": final}, cache_file_path)
            return dt.fromtimestamp(final)
        except BaseException as e:
            raise Exception(
                "Failed to get the last update time of AnimeAPI's database, reason: " +
                str(e))

    async def get_relation(
        self,
        media_id: str | int,
        platform: AnimeApiPlatforms
        | Literal[
            "anisearch",
            "anidb",
            "anilist",
            "animeplanet",
            "annict",
            "kaize",
            "kitsu",
            "livechart",
            "myanimelist",
            "notify",
            "otakotaku",
            "shikimori",
            "shoboi",
            "silveryasha",
            "trakt",
        ],
    ) -> AnimeApiAnime:
        """
        Get a relation between anime and other platform via Natsu's AniAPI

        Args:
            media_id (str | int): Anime ID
            platform (AnimeApiPlatforms | Literal["anisearch", "anidb", "anilist", "animeplanet", "annict", "kaize", "kitsu", "livechart", "myanimelist", "notify", "otakotaku", "shikimori", "shoboi", "silveryasha", "trakt" ]): Platform to get the relation

        Returns:
            AnimeApiAnime: Relation between anime and other platform
        """
        if isinstance(platform, self.AnimeApiPlatforms):
            platform = platform.value
        cache_file_path = Cache.get_cache_file_path(
            f"{platform}/{media_id}.json")
        cached_data = Cache.read_cached_data(cache_file_path)
        if cached_data is not None:
            return AnimeApiAnime(**cached_data)
        try:
            async with self.session.get(
                f"https://aniapi.nattadasu.my.id/{platform}/{media_id}"
            ) as resp:
                jsonText = await resp.text()
                jsonText = json.loads(jsonText)
                Cache.write_data_to_cache(jsonText, cache_file_path)
            return AnimeApiAnime(**jsonText)
        except BaseException:
            return AnimeApiAnime()


__all__ = ["AnimeApi", "AnimeApiAnime"]
