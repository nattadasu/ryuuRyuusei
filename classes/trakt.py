import json
from dataclasses import dataclass
from enum import Enum
from typing import Literal

import aiohttp

from classes.cache import Caching
from classes.excepts import ProviderHttpError, ProviderTypeError
from modules.const import USER_AGENT, traktHeader

Cache = Caching("cache/trakt", 86400)


@dataclass
class TraktIdsStruct:
    """Trakt IDs dataclass"""

    trakt: int
    """Trakt ID"""
    slug: str
    """Trakt slug"""
    imdb: str | None = None
    """IMDB ID"""
    tmdb: int | None = None
    """TMDB ID"""
    tvdb: int | None = None
    """TVDB ID"""
    tvrage: dict | int | str | None = None
    """TVRage ID"""


@dataclass
class TraktMediaStruct:
    """Trakt Media dataclass"""

    title: str
    """Media title"""
    year: int
    """Media year"""
    ids: TraktIdsStruct
    """Media IDs"""


@dataclass
class TraktLookupStruct:
    """Trakt Lookup dataclass"""

    type: Literal["movie", "show"]
    """Media type"""
    score: float | None
    """Media score"""
    movie: TraktMediaStruct | None = None
    """Movie data"""
    show: TraktMediaStruct | None = None
    """Show data"""


@dataclass
class TraktAirStruct:
    """Trakt Air dataclass"""

    day: str | None
    """Day of the week"""
    time: str | None
    """Time of the day"""
    timezone: str | None
    """Timezone"""


@dataclass
class TraktExtendedShowStruct(TraktMediaStruct):
    """Trakt Extended Show dataclass"""

    overview: str | None
    """Show overview"""
    first_aired: str | None
    """First aired date"""
    airs: TraktAirStruct | None
    """Show air data"""
    runtime: int | None
    """Show runtime"""
    certification: str | None
    """Show certification"""
    network: str | None
    """Show network"""
    country: str | None
    """Show country"""
    trailer: str | None
    """Show trailer"""
    updated_at: str | None
    """Show last updated date"""
    homepage: str | None
    """Show homepage"""
    status: Literal[
        "returning series",
        "continuing",
        "in production",
        "planned",
        "canceled",
        "ended",
        "pilot",
    ]
    """Show status"""
    rating: float | None
    """Show rating"""
    votes: int | None
    """Show votes"""
    comment_count: int | None
    """Show comment count"""
    language: str | None
    """Show language"""
    available_translations: list[str] | None
    """Show available translations"""
    genres: list[str] | None
    """Show genres"""
    aired_episodes: int | None
    """Show aired episodes"""


@dataclass
class TraktExtendedMovieStruct(TraktMediaStruct):
    """Trakt Extended Movie dataclass"""

    tagline: str | None
    """Movie tagline"""
    overview: str | None
    """Movie overview"""
    released: str | None
    """Movie release date"""
    runtime: int | None
    """Movie runtime"""
    country: str | None
    """Movie country"""
    updated_at: str | None
    """Movie last updated date"""
    trailer: str | None
    """Movie trailer"""
    homepage: str | None
    """Movie homepage"""
    status: Literal["released", "in production",
                    "post production", "planned", "rumored", "canceled"]
    """Movie status"""
    rating: float | None
    """Movie rating"""
    votes: int | None
    """Movie votes"""
    comment_count: int | None
    """Movie comment count"""
    language: str | None
    """Movie language"""
    available_translations: list[str] | None
    """Movie available translations"""
    genres: list[str] | None
    """Movie genres"""
    certification: str | None
    """Movie certification"""
    airs: None = None
    """Movie air data, placeholder for compatibility (always None) due to unknown bug happened"""


class Trakt:
    """Trakt API Wrapper"""

    def __init__(self, headers: dict | None = None):
        """
        Initialize the Trakt API Wrapper

        Args:
            headers (dict): Trakt API headers, defaults to traktHeader on modules/const.py
        """
        if headers is None:
            headers = traktHeader
        self.base_url = "https://api.trakt.tv/"
        if headers is None:
            self.headers = traktHeader
        else:
            self.headers = headers
        self.headers["User-Agent"] = USER_AGENT
        self.session = aiohttp.ClientSession(headers=self.headers)

    async def __aenter__(self):
        """Enter the async context manager"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context manager"""
        await self.close()

    async def close(self):
        """Close the aiohttp session"""
        await self.session.close()

    class Platform(Enum):
        """Supported Platform Enum"""

        IMDB = "imdb"
        TMDB = "tmdb"

    class MediaType(Enum):
        """Media type enum"""

        TV = SHOW = SHOWS = ONA = "shows"
        MOVIE = MOVIES = "movies"

    @staticmethod
    def ids_dict_to_dataclass(
        data: list[
            dict[
                str,
                str | float | dict | None,
            ]
        ],
    ) -> list[TraktLookupStruct]:
        """
        Convert a dict of IDs to a dataclass

        Args:
            data (list[dict[str, str | float | dict | None]]): List of IDs

        Returns:
            list[TraktLookupStruct]: List of converted dataclass
        """
        converted_data = []
        for x in data:
            if x.get("movie", None):
                x["movie"]["ids"] = TraktIdsStruct(**x["movie"]["ids"])
                x["movie"] = TraktMediaStruct(**x["movie"])
            if x.get("show", None):
                x["show"]["ids"] = TraktIdsStruct(**x["show"]["ids"])
                x["show"] = TraktMediaStruct(**x["show"])
            converted_data.append(
                TraktLookupStruct(
                    type=x["type"],
                    score=x["score"],
                    movie=x.get("movie", None),
                    show=x.get("show", None),
                )
            )
        return converted_data

    def extended_dict_to_dataclass(
        self, data: dict, media_type: MediaType
    ) -> TraktExtendedMovieStruct | TraktExtendedShowStruct:
        """
        Convert a dict of extended information to a dataclass

        Args:
            data (dict): Dict of extended information
            media_type (MediaType): Media type

        Returns:
            TraktExtendedMovieStruct | TraktExtendedShowStruct: Converted dataclass
        """
        data["ids"] = TraktIdsStruct(**data["ids"])
        if media_type == self.MediaType.SHOWS and data.get("airs", None):
            data["airs"] = TraktAirStruct(**data["airs"])
        else:
            data["airs"] = None
        if media_type == self.MediaType.SHOWS:
            return TraktExtendedShowStruct(**data)
        return TraktExtendedMovieStruct(**data)

    async def lookup(
        self,
        media_id: int | str,
        platform: Platform = Platform.IMDB,
        media_type: MediaType = MediaType.TV,
    ) -> TraktLookupStruct:
        """
        Lookup a TV show or movie by ID on a supported platform

        Args:
            id (int | str): The ID of the TV show or movie
            platform (Platform): The supported platform, defaults to Platform.IMDB
            media_type (MediaType): The media type for TMDB, defaults to MediaType.TV

        Raises:
            ProviderTypeError: If the platform is TMDB and the media type is not specified
            ProviderHttpError: If the HTTP request fails

        Returns:
            TraktIdsStruct: The lookup result
        """
        if platform == self.Platform.TMDB and not media_type:
            raise ProviderTypeError("TMDB requires a media type", "MediaType")
        cache_file_path = Cache.get_cache_path(
            f"lookup/{platform.value}/{media_type.value}/{media_id}.json"
        )
        cached_data = Cache.read_cache(cache_file_path, 2592000)
        if cached_data is not None:
            ids = self.ids_dict_to_dataclass(cached_data)
            return ids[0]
        if platform == self.Platform.TMDB:
            params = {"type": media_type.value}
        else:
            params = {}
        url = f"{self.base_url}search/{platform.value}/{media_id}"
        async with self.session.get(url, params=params) as resp:
            if resp.status != 200:
                raise ProviderHttpError(resp.text(), resp.status)
            jsonText = await resp.text()
            jsonFinal = json.loads(jsonText)
        Cache.write_cache(cache_file_path, jsonFinal)
        ids = self.ids_dict_to_dataclass(jsonFinal)
        return ids[0]

    async def get_title_data(
        self, media_id: int | str, media_type: MediaType
    ) -> TraktExtendedMovieStruct | TraktExtendedShowStruct:
        """
        Get the data of a TV show or movie by ID

        Args:
            media_id (int | str): The ID of the TV show or movie
            media_type (MediaType): The media type

        Raises:
            ProviderHttpError: If the HTTP request fails

        Returns:
            TraktExtendedMovieStruct | TraktExtendedShowStruct: The data of the TV show or movie
        """
        cache_file_path = Cache.get_cache_path(
            f"{media_type.value}/{media_id}.json")
        cached_data = Cache.read_cache(cache_file_path)
        if cached_data is not None:
            return self.extended_dict_to_dataclass(cached_data, media_type)
        url = f"{self.base_url}{media_type.value}/{media_id}"
        param = {"extended": "full"}
        async with self.session.get(url, params=param) as resp:
            if resp.status != 200:
                raise ProviderHttpError(resp.text(), resp.status)
            jsonText = await resp.text()
            jsonFinal = json.loads(jsonText)
        Cache.write_cache(cache_file_path, jsonFinal)
        return self.extended_dict_to_dataclass(jsonFinal, media_type)


__all__ = [
    "Trakt",
    "TraktExtendedMovieStruct",
    "TraktExtendedShowStruct",
    "TraktIdsStruct",
]
