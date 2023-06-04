"""AniList Asynchronous API Wrapper"""
import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal

from aiohttp import ClientSession

from classes.excepts import ProviderHttpError, ProviderTypeError
from modules.const import USER_AGENT, ANILIST_ACCESS_TOKEN, ANILIST_OAUTH_EXPIRY


@dataclass
class AniListTitleStruct:
    """AniList title dataclass"""

    romaji: str | None = None
    """Romaji title"""
    english: str | None = None
    """English title"""
    native: str | None = None
    """Native title"""


@dataclass
class AniListDateStruct:
    """AniList date dataclass"""

    year: int | None = None
    """Year"""
    month: int | None = None
    """Month"""
    day: int | None = None
    """Day"""


@dataclass
class AniListImageStruct:
    """AniList image dataclass"""

    medium: str | None = None
    """Medium image URL"""
    large: str | None = None
    """Large image URL"""
    extraLarge: str | None = None
    """Extra large image URL"""
    color: str | None = None
    """Average HEX ("#RRGGBB") color of the image"""


@dataclass
class AniListTagsStruct:
    """AniList tags dataclass"""

    id: int
    """Tag ID"""
    name: str
    """Tag name"""
    isMediaSpoiler: bool | None = None
    """Whether the tag is a spoiler for this media"""
    isAdult: bool | None = None
    """Whether the tag is only for adult 18+ media"""


@dataclass
class AniListTrailerStruct:
    """AniList trailer dataclass"""

    id: str | None = None
    """Trailer ID"""
    site: str | None = None
    """Trailer site, commonly "youtube" or "dailymotion"."""


@dataclass
class AniListMediaStruct:
    """AniList media dataclass"""

    id: int
    """Media ID"""
    idMal: int | None = None
    """MyAnimeList ID"""
    title: AniListTitleStruct | None = None
    """Media title object"""
    isAdult: bool | None = None
    """Whether the media is 18+"""
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
    ] | None = None
    """Media format"""
    description: str | None = None
    """Media description"""
    isAdult: bool | None = None
    """Whether the media is 18+"""
    synonyms: list[str | None] | None = None
    """Media synonyms"""
    startDate: AniListDateStruct | None = None
    """Media start date"""
    endDate: AniListDateStruct | None = None
    """Media end date"""
    status: Literal[
        "FINISHED", "RELEASING", "NOT_YET_RELEASED", "CANCELLED", "HIATUS"
    ] | None = None
    """Media release status"""
    coverImage: AniListImageStruct | None = None
    """Media cover/poster/visual key image object"""
    bannerImage: str | None = None
    """Media banner image URL"""
    genres: list[str | None] | None = None
    """Media genres"""
    tags: list[AniListTagsStruct] | None = None
    """Media tags/themes"""
    averageScore: int | None = None
    """Media weighted average score"""
    meanScore: int | None = None
    """Media mean score"""
    stats: dict[str, list[dict[str, Any] | None]] | None = None
    """Media statistics, doesn't set as dataclass because it's a nested dictionary"""
    trailer: AniListTrailerStruct | None = None
    """Media trailer object"""
    siteUrl: str | None = None
    """Media AniList URL"""
    chapters: int | None = None
    """Manga chapters"""
    volumes: int | None = None
    """Manga volumes"""
    episodes: int | None = None
    """Anime episodes"""
    duration: int | None = None
    """Anime episode duration in minutes"""


@dataclass
class AniListStatusBase:
    """Base AniList status dataclass"""

    status: Literal[
        "CURRENT", "PLANNING", "COMPLETED", "DROPPED", "PAUSED", "REPEATING"
    ] | None = None
    """Status"""
    count: int | None = None
    """Status count"""


@dataclass
class AniListStatisticBase:
    """Base AniList statistic dataclass"""

    count: int | None = None
    """Statistic count"""
    meanScore: int | None = None
    """Statistic mean score"""
    statuses: list[AniListStatusBase] | None = None
    """Statistic statuses"""


@dataclass
class AniListAnimeStatistic(AniListStatisticBase):
    """AniList anime statistic dataclass"""

    minutesWatched: int | None = None
    """Minutes watched"""
    episodesWatched: int | None = None
    """Episodes watched"""


@dataclass
class AniListMangaStatistic(AniListStatisticBase):
    """AniList manga statistic dataclass"""

    chaptersRead: int | None = None
    """Chapters read"""
    volumesRead: int | None = None
    """Volumes read"""


@dataclass
class AniListUserStatisticStruct:
    """AniList user statistic dataclass"""

    anime: AniListAnimeStatistic | None = None
    """Anime statistic object"""
    manga: AniListMangaStatistic | None = None
    """Manga statistic object"""


@dataclass
class AniListUserMediaNode:
    """AniList user media node dataclass"""

    nodes: list[AniListMediaStruct] | None = None


@dataclass
class AniListUserFavoriteStruct:
    """AniList user favorite dataclass"""

    anime: AniListUserMediaNode | None = None
    """Anime favorites"""
    manga: AniListUserMediaNode | None = None
    """Manga favorites"""
    characters: None = None
    """Character favorites"""
    staff: None = None
    """Staff favorites"""
    studios: None = None
    """Studio favorites"""


@dataclass
class AniListUserStruct:
    """AniList user dataclass"""

    id: int
    """User ID"""
    name: str
    """User name"""
    about: str | None = None
    """User about/bio"""
    siteUrl: str | None = None
    """User AniList URL"""
    avatar: AniListImageStruct | None = None
    """User avatar image object"""
    bannerImage: str | None = None
    """User banner image URL"""
    donatorTier: int | None = None
    """User donator tier"""
    donatorBadge: str | None = None
    """User donator badge"""
    createdAt: datetime | None = None
    """User creation date"""
    statistics: AniListUserStatisticStruct | None = None
    """User statistics object"""
    favourites: AniListUserFavoriteStruct | None = None


class AniList:
    """AniList Asynchronous API Wrapper"""

    def __init__(self):
        """Initialize the AniList API Wrapper"""
        self.base_url = "https://graphql.anilist.co"
        self.session = None
        self.headers = None
        self.access_token = ANILIST_ACCESS_TOKEN
        self.cache_directory = "cache/anilist"
        self.cache_expiration_time = 86400  # 1 day in seconds

    async def __aenter__(self):
        """Create the session"""
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        }
        if int(ANILIST_OAUTH_EXPIRY) > datetime.now(tz=timezone.utc).timestamp():
            self.headers["Authorization"] = f"Bearer {self.access_token}"
        else:
            print(
                "[API] [AniList] [WARNING] Access token has expired, please refresh it, otherwise bot won't show NSFW content"
            )
        self.session = ClientSession()
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

    @staticmethod
    def _media_dict_to_dataclass(data: dict):
        """Format returned dictionary from AniList to its proper dataclass"""
        data["title"] = AniListTitleStruct(**data["title"]) if data["title"] else None
        if data.get("startDate", None):
            data["startDate"] = (
                AniListDateStruct(**data["startDate"]) if data["startDate"] else None
            )
        if data.get("endDate", None):
            data["endDate"] = (
                AniListDateStruct(**data["endDate"]) if data["endDate"] else None
            )
        if data.get("coverImage", None):
            data["coverImage"] = (
                AniListImageStruct(**data["coverImage"]) if data["coverImage"] else None
            )
        if data.get("trailer", None):
            data["trailer"] = (
                AniListTrailerStruct(**data["trailer"]) if data["trailer"] else None
            )
        if data.get("tags", None):
            data["tags"] = [AniListTagsStruct(**tag) for tag in data["tags"]]
        return AniListMediaStruct(**data)

    def _user_dict_to_dataclass(self, data: dict) -> AniListUserStruct:
        """
        Format returned dictionary from AniList to its proper dataclass

        Args:
            data (dict): Dictionary to format

        Returns:
            AniListUserStruct: Formatted dataclass
        """
        data["avatar"] = (
            AniListImageStruct(**data["avatar"]) if data["avatar"] else None
        )
        data["createdAt"] = (
            datetime.fromtimestamp(data["createdAt"], timezone.utc)
            if data["createdAt"]
            else None
        )
        if data["statistics"]["anime"]:
            data["statistics"]["anime"]["statuses"] = [
                AniListStatusBase(**status)
                for status in data["statistics"]["anime"]["statuses"]
            ]
            data["statistics"]["anime"] = AniListAnimeStatistic(
                **data["statistics"]["anime"]
            )
        if data["statistics"]["manga"]:
            data["statistics"]["manga"]["statuses"] = [
                AniListStatusBase(**status)
                for status in data["statistics"]["manga"]["statuses"]
            ]
            data["statistics"]["manga"] = AniListMangaStatistic(
                **data["statistics"]["manga"]
            )
        data["statistics"] = (
            AniListUserStatisticStruct(**data["statistics"])
            if data["statistics"]
            else None
        )
        if data["favourites"]["anime"]:
            data["favourites"]["anime"]["nodes"] = [
                self._media_dict_to_dataclass(media)
                for media in data["favourites"]["anime"]["nodes"]
            ]
            data["favourites"]["anime"] = AniListUserMediaNode(
                **data["favourites"]["anime"]
            )
        if data["favourites"]["manga"]:
            data["favourites"]["manga"]["nodes"] = [
                self._media_dict_to_dataclass(media)
                for media in data["favourites"]["manga"]["nodes"]
            ]
            data["favourites"]["manga"] = AniListUserMediaNode(
                **data["favourites"]["manga"]
            )
        data["favourites"] = (
            AniListUserFavoriteStruct(**data["favourites"])
            if data["favourites"]
            else None
        )
        return AniListUserStruct(**data)

    async def nsfw_check(
        self,
        media_id: int,
        media_type: Literal["ANIME", "MANGA"] | MediaType = MediaType.ANIME,
    ) -> bool:
        """
        Check if the media is NSFW

        Args:
            media_id (int): The ID of the media
            media_type (Literal['ANIME', 'MANGA'] | MediaType, optional): The type of the media. Defaults to MediaType.ANIME.

        Raises:
            ProviderHttpError: Raised when the HTTP request fails

        Returns:
            bool: True if the media is NSFW, False if not
        """
        self.cache_expiration_time = 604800
        if isinstance(media_type, str):
            media_type = self.MediaType(media_type)
        media: str = media_type.value
        cache_file_path = self.get_cache_file_path(
            f"nsfw/{media.lower()}/{media_id}.json"
        )
        cached_data = self.read_cached_data(cache_file_path)
        if cached_data is not None:
            return cached_data
        query = f"""query {{
    Media(id: {media_id}, type: {media}) {{
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
        """
        Get anime information by its ID

        Args:
            media_id (int): The ID of the anime

        Raises:
            ProviderHttpError: Raised when the HTTP request fails

        Returns:
            AniListMediaStruct: The anime information
        """
        cache_file_path = self.get_cache_file_path(f"anime/{media_id}.json")
        cached_data = self.read_cached_data(cache_file_path)
        if cached_data is not None:
            return self._media_dict_to_dataclass(cached_data)
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
                return self._media_dict_to_dataclass(data["data"]["Media"])
            error_message = await response.text()
            raise ProviderHttpError(error_message, response.status)

    async def manga(self, media_id: int) -> AniListMediaStruct:
        """
        Get manga information by its ID

        Args:
            media_id (int): The ID of the manga

        Returns:
            AniListMediaStruct: The manga information
        """
        cache_file_path = self.get_cache_file_path(f"manga/{media_id}.json")
        cached_data = self.read_cached_data(cache_file_path)
        if cached_data is not None:
            return self._media_dict_to_dataclass(cached_data)
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
                return self._media_dict_to_dataclass(data["data"]["Media"])
            error_message = await response.text()
            raise ProviderHttpError(error_message, response.status)

    async def user(self, username: str, return_id: bool = False) -> AniListUserStruct:
        """
        Get user information by their username

        Args:
            username (str): The username of the user
            return_id (bool, optional): Whether to return the user ID or not. Defaults to False.

        Raises:
            ProviderHttpError: Raised when the HTTP request fails

        Returns:
            AniListUserStruct: The user information
        """
        self.cache_expiration_time = 43200
        cache_file_path = self.get_cache_file_path(f"user/{username}.json")
        cached_data = self.read_cached_data(cache_file_path)
        if cached_data is not None and not return_id:
            formatted_data = self._user_dict_to_dataclass(cached_data)
            return formatted_data
        if return_id:
            gqlquery = f"""query {{
    User(name: "{username}") {{
        id
    }}
}}"""
        else:
            gqlquery = f"""query {{
    User(name: "{username}") {{
        id
        name
        about
        avatar {{
            large
            medium
        }}
        bannerImage
        statistics {{
            anime {{
                count
                meanScore
                minutesWatched
                episodesWatched
                statuses{{
                    count
                    status
                }}
            }}
            manga {{
                count
                meanScore
                chaptersRead
                volumesRead
                statuses{{
                    count
                    status
                }}
            }}
        }}
        favourites {{
            anime(perPage:5){{
                nodes {{
                    id
                    title {{
                        romaji
                        english
                        native
                    }}
                    siteUrl
                }}
            }}
            manga(perPage:5){{
                nodes {{
                    id
                    title {{
                        romaji
                        english
                        native
                    }}
                    siteUrl
                }}
            }}
        }}
        siteUrl
        donatorTier
        donatorBadge
        createdAt
    }}
}}"""
        async with self.session.post(
            self.base_url, json={"query": gqlquery}
        ) as response:
            if response.status == 200:
                data = await response.json()
                user_data = data["data"]["User"]
                if not return_id:
                    self.write_data_to_cache(user_data, cache_file_path)
                    formatted_data = self._user_dict_to_dataclass(user_data)
                else:
                    formatted_data = AniListUserStruct(
                        id=user_data["id"],
                        name=username,
                    )
                return formatted_data
            error_message = await response.text()
            raise ProviderHttpError(error_message, response.status)

    async def search_media(
        self,
        query: str,
        limit: int = 10,
        media_type: Literal["ANIME", "MANGA"] | MediaType = MediaType.MANGA,
    ) -> list[dict]:
        """
        Search anime by its title

        Args:
            query (str): The title of the anime
            limit (int, optional): The number of results to return. Defaults to 10
            media_type (Literal['ANIME', 'MANGA'] | MediaType, optional): The type of the media. Defaults to MediaType.MANGA

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
            status
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
        """
        Get cache file path

        Args:
            cache_file_name (str): Cache file name

        Returns:
            str: Cache file path
        """
        return os.path.join(self.cache_directory, cache_file_name)

    def read_cached_data(self, cache_file_path: str) -> Any | None:
        """
        Read cached data

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
        """
        Write data to cache

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
