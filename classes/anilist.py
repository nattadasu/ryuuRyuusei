"""AniList Asynchronous API Wrapper"""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal

from aiohttp import ClientSession
from dacite import Config, from_dict

from classes.cache import Caching
from classes.excepts import ProviderHttpError, ProviderTypeError
from modules.const import ANILIST_ACCESS_TOKEN, ANILIST_OAUTH_EXPIRY, USER_AGENT

Cache = Caching(cache_directory="cache/anilist", cache_expiration_time=86400)


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
    # pylint: disable-next=invalid-name
    extraLarge: str | None = None
    """Extra large image URL"""
    color: str | None = None
    """Average HEX ("#RRGGBB") color of the image"""


@dataclass
class AniListTagsStruct:
    """AniList tags dataclass"""

    # pylint: disable-next=invalid-name
    id: int
    """Tag ID"""
    name: str
    """Tag name"""
    # pylint: disable-next=invalid-name
    isMediaSpoiler: bool | None = None
    """Whether the tag is a spoiler for this media"""
    # pylint: disable-next=invalid-name
    isAdult: bool | None = None
    """Whether the tag is only for adult 18+ media"""


@dataclass
class AniListTrailerStruct:
    """AniList trailer dataclass"""

    # pylint: disable-next=invalid-name
    id: str | None = None
    """Trailer ID"""
    site: str | None = None
    """Trailer site, commonly "youtube" or "dailymotion"."""


@dataclass
class AniListMediaStruct:
    """AniList media dataclass"""

    # pylint: disable-next=invalid-name
    id: int
    """Media ID"""
    # pylint: disable-next=invalid-name
    idMal: int | None = None
    """MyAnimeList ID"""
    title: AniListTitleStruct | None = None
    """Media title object"""
    # pylint: disable-next=invalid-name
    isAdult: bool | None = None
    """Whether the media is 18+"""
    format: (
        Literal[
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
        ]
        | None
    ) = None
    """Media format"""
    description: str | None = None
    """Media description"""
    # pylint: disable-next=invalid-name
    isAdult: bool | None = None
    """Whether the media is 18+"""
    synonyms: list[str | None] | None = None
    """Media synonyms"""
    # pylint: disable-next=invalid-name
    startDate: AniListDateStruct | None = None
    """Media start date"""
    # pylint: disable-next=invalid-name
    endDate: AniListDateStruct | None = None
    """Media end date"""
    status: (
        Literal["FINISHED", "RELEASING", "NOT_YET_RELEASED", "CANCELLED", "HIATUS"]
        | None
    ) = None
    """Media release status"""
    # pylint: disable-next=invalid-name
    coverImage: AniListImageStruct | None = None
    """Media cover/poster/visual key image object"""
    # pylint: disable-next=invalid-name
    bannerImage: str | None = None
    """Media banner image URL"""
    genres: list[str | None] | None = None
    """Media genres"""
    tags: list[AniListTagsStruct] | None = None
    """Media tags/themes"""
    # pylint: disable-next=invalid-name
    averageScore: int | None = None
    """Media weighted average score"""
    # pylint: disable-next=invalid-name
    meanScore: float | None = None
    """Media mean score"""
    stats: dict[str, list[dict[str, Any] | None]] | None = None
    """Media statistics, doesn't set as dataclass because it's a nested dictionary"""
    trailer: AniListTrailerStruct | None = None
    """Media trailer object"""
    # pylint: disable-next=invalid-name
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

    status: (
        Literal["CURRENT", "PLANNING", "COMPLETED", "DROPPED", "PAUSED", "REPEATING"]
        | None
    ) = None
    """Status"""
    count: int | None = None
    """Status count"""


@dataclass
class AniListStatisticBase:
    """Base AniList statistic dataclass"""

    count: int | None = None
    """Statistic count"""
    # pylint: disable-next=invalid-name
    meanScore: float | None = None
    """Statistic mean score"""
    statuses: list[AniListStatusBase] | None = None
    """Statistic statuses"""


@dataclass
class AniListAnimeStatistic(AniListStatisticBase):
    """AniList anime statistic dataclass"""

    # pylint: disable-next=invalid-name
    minutesWatched: int | None = None
    """Minutes watched"""
    # pylint: disable-next=invalid-name
    episodesWatched: int | None = None
    """Episodes watched"""


@dataclass
class AniListMangaStatistic(AniListStatisticBase):
    """AniList manga statistic dataclass"""

    # pylint: disable-next=invalid-name
    chaptersRead: int | None = None
    """Chapters read"""
    # pylint: disable-next=invalid-name
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

    # pylint: disable-next=invalid-name
    id: int
    """User ID"""
    name: str
    """User name"""
    about: str | None = None
    """User about/bio"""
    # pylint: disable-next=invalid-name
    siteUrl: str | None = None
    """User AniList URL"""
    avatar: AniListImageStruct | None = None
    """User avatar image object"""
    moderatorRoles: list[str] | None = None
    """List of moderation roles user get on the site"""
    # pylint: disable-next=invalid-name
    bannerImage: str | None = None
    """User banner image URL"""
    # pylint: disable-next=invalid-name
    donatorTier: int | None = None
    """User donator tier"""
    # pylint: disable-next=invalid-name
    donatorBadge: str | None = None
    """User donator badge"""
    # pylint: disable-next=invalid-name
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
        self.session = ClientSession()
        self.headers = None
        self.access_token = ANILIST_ACCESS_TOKEN

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
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        """Close the session"""
        await self.close()

    async def close(self) -> None:
        """Close aiohttp session"""
        await self.session.close()  # type: ignore

    class MediaType(Enum):
        """Media type enum for AniList"""

        ANIME = "ANIME"
        MANGA = "MANGA"

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
        if isinstance(media_type, str):
            media_type = self.MediaType(media_type)
        media: str = media_type.value
        cache_file_path = Cache.get_cache_file_path(
            f"nsfw/{media.lower()}/{media_id}.json"
        )
        cached_data = Cache.read_cached_data(
            cache_file_path, override_expiration_time=604800
        )
        if cached_data is not None:
            return cached_data
        query = f"""query {{
    Media(id: {media_id}, type: {media}) {{
        id
        isAdult
    }}
}}"""
        async with self.session.post(self.base_url, json={"query": query}) as response:
            try:
                data: dict[str, Any] = await response.json()
            # pylint: disable-next=broad-except
            except Exception as err:
                raise ProviderHttpError(str(err), response.status) from err
            errors: list[dict[str, Any]] | None = data.get("errors", None)
            if errors:
                err_strings: str = "\n".join(
                    [
                        f"- [{err['status']}] {err['message']}{' Hint:' + err['hint'] if err.get('hint', None) else ''}"
                        for err in errors
                    ]
                )
                raise ProviderHttpError(err_strings, response.status)
            Cache.write_data_to_cache(data["data"]["Media"]["isAdult"], cache_file_path)
            return data["data"]["Media"]["isAdult"]

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
        cache_file_path = Cache.get_cache_file_path(f"anime/{media_id}.json")
        cached_data = Cache.read_cached_data(cache_file_path)
        if cached_data is not None:
            # return self._media_dict_to_dataclass(cached_data)
            return from_dict(AniListMediaStruct, cached_data)
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
            try:
                data: dict[str, Any] = await response.json()
            except Exception as err:
                raise ProviderHttpError(str(err), response.status) from err
            errors: list[dict[str, Any]] | None = data.get("errors", None)
            if errors:
                err_strings: str = "\n".join(
                    [
                        f"- [{err['status']}] {err['message']}{' Hint:' + err['hint'] if err.get('hint', None) else ''}"
                        for err in errors
                    ]
                )
                raise ProviderHttpError(err_strings, response.status)
            Cache.write_data_to_cache(data["data"]["Media"], cache_file_path)
            return from_dict(AniListMediaStruct, data["data"]["Media"])

    async def manga(self, media_id: int, from_mal: bool = False) -> AniListMediaStruct:
        """
        Get manga information by its ID

        Args:
            media_id (int): The ID of the manga
            from_mal (bool, optional): Whether the ID is from MyAnimeList or not. Defaults to False.

        Returns:
            AniListMediaStruct: The manga information
        """
        cache_file_path = Cache.get_cache_file_path(f"manga/{media_id}.json")
        cached_data = Cache.read_cached_data(cache_file_path)
        if cached_data is not None:
            return from_dict(AniListMediaStruct, cached_data)
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
        siteUrl
        trailer {{
            id
            site
        }}
    }}
}}"""
        if from_mal:
            # replace Media(id: to Media(idMal:
            gqlquery = gqlquery.replace("Media(id:", "Media(idMal:")
        async with self.session.post(
            self.base_url, json={"query": gqlquery}
        ) as response:
            try:
                data: dict[str, Any] = await response.json()
            except Exception as err:
                raise ProviderHttpError(str(err), response.status) from err
            errors: list[dict[str, Any]] | None = data.get("errors", None)
            if errors:
                err_strings: str = "\n".join(
                    [
                        f"- [{err['status']}] {err['message']}{' Hint:' + err['hint'] if err.get('hint', None) else ''}"
                        for err in errors
                    ]
                )
                raise ProviderHttpError(err_strings, response.status)
            media_data = data["data"]["Media"]
            # Handle None scoreDistribution by converting to empty list
            if (
                media_data.get("stats")
                and media_data["stats"].get("scoreDistribution") is None
            ):
                media_data["stats"]["scoreDistribution"] = []
            Cache.write_data_to_cache(media_data, cache_file_path)
            return from_dict(AniListMediaStruct, media_data)

    async def user_by_id(
        self, user_id: int, return_as_is: bool = False
    ) -> AniListUserStruct:
        """
        Get user information by their ID

        Args:
            user_id (int): The ID of the user
            return_as_is (bool, optional): Whether to return the data as is or further processed. Defaults to False.

        Raises:
            ProviderHttpError: Raised when the HTTP request fails

        Returns:
            AniListUserStruct: The user information
        """
        config = Config(
            type_hooks={
                datetime: lambda value: datetime.fromtimestamp(value, timezone.utc)
            }
        )
        gqlquery = f"""query {{
    User (id: {user_id}) {{
        id
        name
    }}
}}"""
        async with self.session.post(
            self.base_url, json={"query": gqlquery}
        ) as response:
            try:
                response.raise_for_status()
                data: dict[str, Any] = await response.json()
            except Exception as err:
                raise ProviderHttpError(str(err), response.status) from err
            errors: list[dict[str, Any]] | None = data.get("errors", None)
            if errors:
                err_strings: str = "\n".join(
                    [
                        f"- [{err['status']}] {err['message']}{' Hint:' + err['hint'] if err.get('hint', None) else ''}"
                        for err in errors
                    ]
                )
                raise ProviderHttpError(err_strings, response.status)
            user_data = data["data"]["User"]
        if return_as_is:
            return from_dict(AniListUserStruct, user_data, config=config)
        return await self.user(user_data["name"])

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
        cache_file_path = Cache.get_cache_file_path(f"user/{username}.json")
        cached_data = Cache.read_cached_data(cache_file_path, 43200)
        config = Config(
            type_hooks={
                datetime: lambda value: datetime.fromtimestamp(value, timezone.utc)
            }
        )
        if cached_data is not None and not return_id:
            return from_dict(AniListUserStruct, cached_data, config=config)
        if return_id:
            gqlquery = f"""query {{
    User(name: "{username}") {{
        id
        name
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
        moderatorRoles
    }}
}}"""
        async with self.session.post(
            self.base_url, json={"query": gqlquery}
        ) as response:
            try:
                data: dict[str, Any] = await response.json()
            except Exception as err:
                raise ProviderHttpError(str(err), response.status) from err
            errors: list[dict[str, Any]] | None = data.get("errors", None)
            if errors:
                err_strings: str = "\n".join(
                    [
                        f"- [{err['status']}] {err['message']}{' Hint:' + err['hint'] if err.get('hint', None) else ''}"
                        for err in errors
                    ]
                )
                raise ProviderHttpError(err_strings, response.status)
            user_data = data["data"]["User"]
            if not return_id:
                Cache.write_data_to_cache(user_data, cache_file_path)
            return from_dict(AniListUserStruct, user_data, config=config)

    async def search_media(
        self,
        query: str,
        limit: int = 10,
        media_type: Literal["ANIME", "MANGA"] | MediaType = MediaType.MANGA,
    ) -> list[dict[str, Any]]:
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
            list[dict[str, Any]]: The search results
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
            try:
                data: dict[str, Any] = await response.json()
            except Exception as err:
                raise ProviderHttpError(str(err), response.status) from err
            errors: list[dict[str, Any]] | None = data.get("errors", None)
            if errors:
                err_strings: str = "\n".join(
                    [
                        f"- [{err['status']}] {err['message']}{' Hint:' + err['hint'] if err.get('hint', None) else ''}"
                        for err in errors
                    ]
                )
                raise ProviderHttpError(err_strings, response.status)
            return data["data"]["Page"]["results"]


__all__ = ["AniList"]
