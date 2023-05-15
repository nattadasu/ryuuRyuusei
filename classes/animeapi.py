import json
import os
import time
from datetime import datetime as dt
from enum import Enum
from typing import Literal
from dataclasses import dataclass, asdict

from aiohttp import ClientSession

from modules.const import USER_AGENT

@dataclass
class AnimeApiAnime:
    title: str | None = None
    anidb: int | None = None
    anilist: int | None = None
    animeplanet: str | None = None
    anisearch: int | None = None
    annict: int | None = None
    kaize: str | None = None
    kitsu: int | None = None
    livechart: int | None = None
    myanimelist: int | None = None
    notify: str | None = None
    otakotaku: int | None = None
    shikimori: int | None = None
    shoboi: int | None = None
    silveryasha: int | None = None
    trakt: int | None = None
    trakt_type: Literal["shows", "movies"] | None = None
    trakt_season: int | None = None

    def to_dict(self):
        return asdict(self)


class AnimeApi:
    def __init__(self):
        """Initialize the AniAPI API Wrapper"""
        self.base_url = "https://aniapi.nattadasu.my.id"
        self.session = None
        self.cache_directory = "cache/animeapi"
        self.cache_expiration_time = 86400  # 1 day in seconds

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
        """Get the last update time of AniAPI's database

        Returns:
            datetime: The last update time of AniAPI's database
        """
        cache_file_path = self.get_cache_file_path("updated")
        cached_data = self.read_cached_data(cache_file_path)
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
                self.write_data_to_cache({"timestamp": final}, cache_file_path)
            return dt.fromtimestamp(final)
        except BaseException as e:
            raise Exception("Failed to get the last update time of AnimeAPI's database, reason: " + str(e))

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
        """Get a relation between anime and other platform via Natsu's AniAPI

        Args:
            media_id (str | int): Anime ID
            platform (AnimeApiPlatforms | Literal["anisearch", "anidb", "anilist", "animeplanet", "annict", "kaize", "kitsu", "livechart", "myanimelist", "notify", "otakotaku", "shikimori", "shoboi", "silveryasha", "trakt" ]): Platform to get the relation

        Returns:
            AnimeApiAnime: Relation between anime and other platform
        """
        if isinstance(platform, self.AnimeApiPlatforms):
            platform = platform.value
        cache_file_path = self.get_cache_file_path(f"{platform}/{media_id}.json")
        cached_data = self.read_cached_data(cache_file_path)
        if cached_data is not None:
            return AnimeApiAnime(**cached_data)
        try:
            async with self.session.get(
                f"https://aniapi.nattadasu.my.id/{platform}/{media_id}"
            ) as resp:
                jsonText = await resp.text()
                jsonText = json.loads(jsonText)
                self.write_data_to_cache(jsonText, cache_file_path)
            return AnimeApiAnime(**jsonText)
        except BaseException:
            return AnimeApiAnime()

    def get_cache_file_path(self, cache_file_name: str) -> str:
        """Get cache file path

        Args:
            cache_file_name (str): Cache file name

        Returns:
            str: Cache file path
        """
        return os.path.join(self.cache_directory, cache_file_name)

    def read_cached_data(self, cache_file_path: str) -> dict | None:
        """Read cached data

        Args:
            cache_file_name (str): Cache file name

        Returns:
            dict: Cached data
            None: If cache file does not exist
        """
        if os.path.exists(cache_file_path):
            with open(cache_file_path, "r") as cache_file:
                cache_data = json.load(cache_file)
                cache_age = time.time() - cache_data["timestamp"]
                if cache_age < self.cache_expiration_time:
                    return cache_data["data"]
        return None

    @staticmethod
    def write_data_to_cache(data, cache_file_path: str):
        """Write data to cache

        Args:
            data (any): Data to write to cache
            cache_file_name (str): Cache file name
        """
        cache_data = {"timestamp": time.time(), "data": data}
        os.makedirs(os.path.dirname(cache_file_path), exist_ok=True)
        with open(cache_file_path, "w") as cache_file:
            json.dump(cache_data, cache_file)


__all__ = ["AnimeApi", "AnimeApiAnime"]
