"""AniList Asynchronous API Wrapper"""
import json
import os
import time
from enum import Enum
from typing import Literal, Any
from dataclasses import dataclass

from aiohttp import ClientSession

from classes.excepts import ProviderHttpError, ProviderTypeError

from modules.const import USER_AGENT


@dataclass
class AniListTitleStruct:
    romaji: str | None
    english: str | None
    native: str | None


@dataclass
class AniListDateStruct:
    year: int | None
    month: int | None
    day: int | None


@dataclass
class AniListImageStruct:
    large: str | None
    extraLarge: str | None
    color: str | None


@dataclass
class AniListTagsStruct:
    id: int
    name: str
    isMediaSpoiler: bool | None
    isAdult: bool | None


@dataclass
class AniListTrailerStruct:
    id: str | None
    site: str | None


@dataclass
class AniListMediaStruct:
    id: int
    idMal: int | None
    title: AniListTitleStruct | None
    isAdult: bool | None
    format: Literal[
        "TV",
        "TV_SHORT",
        "MOVIE",
        "SPECIAL",
        "OVA",
        "ONA",
        "MUSIC",
        "MANGA",
        "NOVEL",
        "ONE_SHOT",
    ] | None
    description: str | None
    isAdult: bool | None
    synonyms: list[str | None] | None
    startDate: AniListDateStruct | None
    endDate: AniListDateStruct | None
    status: Literal[
        "FINISHED", "RELEASING", "NOT_YET_RELEASED", "CANCELLED", "HIATUS"
    ] | None
    coverImage: AniListImageStruct | None
    bannerImage: str | None
    genres: list[str | None] | None
    tags: list[AniListTagsStruct] | None
    averageScore: int | None
    meanScore: int | None
    stats: dict[str, list[dict[str, Any] | None]] | None
    trailer: AniListTrailerStruct | None
    chapters: int | None = None
    volumes: int | None = None
    episodes: int | None = None
    duration: int | None = None


class AniList:
    """AniList Asynchronous API Wrapper"""

    def __init__(self):
        """Initialize the AniList API Wrapper"""
        self.base_url = "https://graphql.anilist.co"
        self.session = None
        self.cache_directory = "cache/anilist"
        self.cache_expiration_time = 86400  # 1 day in seconds

    async def __aenter__(self):
        """Create the session"""
        self.session = ClientSession(headers={"User-Agent": USER_AGENT})
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Close the session"""
        await self.close()

    async def close(self) -> None:
        """Close aiohttp session"""
        await self.session.close()  # type: ignore

    class MediaType(Enum):
        """Media type enum for AniList"""

        ANIME = "ANIME"
        MANGA = "MANGA"

    def dict_to_dataclass(self, data: dict):
        """Format returned dictionary from AniList to its proper dataclass"""
        data["title"] = AniListTitleStruct(**data["title"]) if data["title"] else None
        data["startDate"] = (
            AniListDateStruct(**data["startDate"]) if data["startDate"] else None
        )
        data["endDate"] = (
            AniListDateStruct(**data["endDate"]) if data["endDate"] else None
        )
        data["coverImage"] = (
            AniListImageStruct(**data["coverImage"]) if data["coverImage"] else None
        )
        data["trailer"] = (
            AniListTrailerStruct(**data["trailer"]) if data["trailer"] else None
        )
        if data["tags"] is not None:
            for tag in data["tags"]:
                tag = AniListTagsStruct(**tag) if tag else None
        return AniListMediaStruct(**data)

    async def nsfwCheck(
        self,
        media_id: int,
        media_type: Literal["ANIME", "MANGA"] | MediaType = MediaType.ANIME,
    ) -> bool:
        """Check if the media is NSFW

        Args:
            media_id (int): The ID of the media
            media_type (Literal['ANIME', 'MANGA'] | MediaType, optional): The type of the media. Defaults to MediaType.ANIME.

        Raises:
            ProviderHttpError: Raised when the HTTP request fails

        Returns:
            bool: True if the media is NSFW, False if not
        """
        self.cache_expiration_time = 604800
        media = ""
        if isinstance(media_type, self.MediaType):
            media = media_type.value
        elif isinstance(media_type, Literal):
            media = media_type
        cache_file_path = self.get_cache_file_path(f"nsfw/{media.lower()}/{id}.json")
        cached_data = self.read_cached_data(cache_file_path)
        if cached_data is not None:
            return cached_data
        query = f"""query {{
    Media(id: {media_id}, type: {media_type}) {{
        id
        isAdult
    }}
}}"""
        async with self.session.post(self.base_url, json={"query": query}) as response:
            if response.status == 200:
                data = await response.json()
                self.write_data_to_cache(
                    data["data"]["Media"]["isAdult"], cache_file_path
                )
                return data["data"]["Media"]["isAdult"]
            error_message = await response.text()
            raise ProviderHttpError(error_message, response.status)

    async def anime(self, media_id: int) -> AniListMediaStruct:
        """Get anime information by its ID

        Args:
            media_id (int): The ID of the anime

        Raises:
            ProviderHttpError: Raised when the HTTP request fails

        Returns:
            dict: The anime information
        """
        cache_file_path = self.get_cache_file_path(f"anime/{media_id}.json")
        cached_data = self.read_cached_data(cache_file_path)
        if cached_data is not None:
            return self.dict_to_dataclass(cached_data)
        gqlquery = f"""query {{
    Media(id: {media_id}, type: ANIME) {{
        id
        idMal
        title {{
            romaji
            english
            native
        }}
        isAdult
        description(asHtml: false)
        synonyms
        format
        startDate {{
            year
            month
            day
        }}
        endDate {{
            year
            month
            day
        }}
        status
        episodes
        duration
        coverImage {{
            large
            extraLarge
            color
        }}
        bannerImage
        genres
        tags {{
            id
            name
            isMediaSpoiler
            isAdult
        }}
        averageScore
        meanScore
        stats {{
            scoreDistribution {{
                score
                amount
            }}
        }}
        trailer {{
            id
            site
        }}
    }}
}}"""
        async with self.session.post(
            self.base_url, json={"query": gqlquery}
        ) as response:
            if response.status == 200:
                data = await response.json()
                self.write_data_to_cache(data["data"]["Media"], cache_file_path)
                return self.dict_to_dataclass(data["data"]["Media"])
            error_message = await response.text()
            raise ProviderHttpError(error_message, response.status)

    async def manga(self, media_id: int) -> AniListMediaStruct:
        """Get manga information by its ID

        Args:
            media_id (int): The ID of the manga

        Returns:
            dict: The manga information
        """
        cache_file_path = self.get_cache_file_path(f"manga/{media_id}.json")
        cached_data = self.read_cached_data(cache_file_path)
        if cached_data is not None:
            return self.dict_to_dataclass(cached_data)
        gqlquery = f"""query {{
    Media(id: {media_id}, type: MANGA) {{
        id
        idMal
        title {{
            romaji
            english
            native
        }}
        isAdult
        description(asHtml: false)
        synonyms
        format
        startDate {{
            year
            month
            day
        }}
        endDate {{
            year
            month
            day
        }}
        status
        chapters
        volumes
        coverImage {{
            extraLarge
            large
            color
        }}
        bannerImage
        genres
        tags {{
            id
            name
            isMediaSpoiler
            isAdult
        }}
        averageScore
        meanScore
        stats {{
            scoreDistribution {{
                score
                amount
            }}
        }}
        trailer {{
            id
            site
        }}
    }}
}}"""
        async with self.session.post(
            self.base_url, json={"query": gqlquery}
        ) as response:
            if response.status == 200:
                data = await response.json()
                self.write_data_to_cache(data["data"]["Media"], cache_file_path)
                return self.dict_to_dataclass(data["data"]["Media"])
            error_message = await response.text()
            raise ProviderHttpError(error_message, response.status)

    async def search_media(
        self,
        query: str,
        limit: int = 10,
        media_type: Literal["ANIME", "MANGA"] | MediaType = MediaType.MANGA,
    ) -> list[dict]:
        """Search anime by its title

        Args:
            query (str): The title of the anime
            limit (int, optional): The number of results to return. Defaults to 10.
            media_type (Literal['ANIME', 'MANGA'] | MediaType, optional): The type of the media. Defaults to MediaType.MANGA.

        Raises:
            ProviderTypeError: Raised when the limit is not valid
            ProviderHttpError: Raised when the HTTP request fails

        Returns:
            list[dict]: The search results
        """
        if limit > 10:
            raise ProviderTypeError("limit must be less than or equal to 10", "int")
        if isinstance(media_type, self.MediaType):
            media_type = media_type.value
        gqlquery = """query ($search: String, $mediaType: MediaType, $limit: Int) {
    Page(page: 1, perPage: $limit) {
        results: media(search: $search, type: $mediaType) {
            id
            idMal
            title {
                romaji
                english
                native
            }
            format
            isAdult
            startDate {
                year
            }
            season
        }
    }
}"""
        variables = {
            "search": query,
            "mediaType": media_type,
            "limit": limit,
        }
        async with self.session.post(
            self.base_url, json={"query": gqlquery, "variables": variables}
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data["data"]["Page"]["results"]
            error_message = await response.text()
            raise ProviderHttpError(error_message, response.status)

    def get_cache_file_path(self, cache_file_name: str) -> str:
        """Get cache file path

        Args:
            cache_file_name (str): Cache file name

        Returns:
            str: Cache file path
        """
        return os.path.join(self.cache_directory, cache_file_name)

    def read_cached_data(self, cache_file_path: str) -> Any | None:
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
    def write_data_to_cache(data, cache_file_path: str) -> None:
        """Write data to cache

        Args:
            data (any): Data to cache
            cache_file_path (str): Cache file path

        Returns:
            None
        """
        cache_data = {"timestamp": time.time(), "data": data}
        os.makedirs(os.path.dirname(cache_file_path), exist_ok=True)
        with open(cache_file_path, "w") as cache_file:
            json.dump(cache_data, cache_file)


__all__ = ["AniList"]
