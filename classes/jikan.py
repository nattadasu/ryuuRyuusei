"""Jikan API Wrapper"""

import asyncio
import traceback
from dataclasses import dataclass, fields
from datetime import datetime
from typing import Any, Literal

from aiohttp import ClientError, ClientSession, ClientTimeout

from classes.cache import Caching
from classes.excepts import ProviderHttpError
from modules.const import JIKAN_URL, USER_AGENT

Cache = Caching(cache_directory="cache/jikan", cache_expiration_time=86400)

REQUEST_TIMEOUT = ClientTimeout(total=30)
"""Per-request timeout so a dead endpoint cannot hang tasks"""

_RETRYABLE_STATUS = {408, 429, 500, 502, 503, 504}
"""HTTP statuses worth retrying with backoff"""


class JikanException(Exception):
    """Exception for Jikan errors"""

    def __init__(self, message, status_code):
        """Params"""
        self.message = message
        self.status_code = status_code

    def __str__(self):
        """String representation"""
        return f"JikanException [{self.status_code}]: {self.message}"


@dataclass
class JikanImageStruct:
    """Jikan Image Struct"""

    image_url: str
    """Standard size image url"""
    small_image_url: str | None = None
    """(very) small image url (usually used for thumbnails)"""
    large_image_url: str | None = None
    """Large image url"""
    medium_image_url: str | None = None
    """Medium image url"""
    maximum_image_url: str | None = None
    """Maximum size image url (usually used for backgrounds)"""


@dataclass
class JikanImages:
    """Jikan Images Type"""

    jpg: JikanImageStruct | None = None
    """JPG image"""
    webp: JikanImageStruct | None = None
    """WebP image"""


@dataclass
class JikanTrailerStruct:
    """Jikan Trailer Struct"""

    youtube_id: str
    """Youtube ID of the trailer"""
    url: str
    """Youtube URL of the trailer"""
    embed_url: str
    """Youtube embed URL of the trailer"""
    images: JikanImages | None
    """Images of the trailer"""


@dataclass
class JikanTitlesStruct:
    """Jikan Titles Struct"""

    type: (
        Literal[
            "Default",
            "Synonym",
            "English",
            "Japanese",
            "German",
            "Spanish",
            "Italian",
            "French",
            "Korean",
            "Portuguese",
            "Chinese",
        ]
        | None
    )
    """Type of the title"""
    title: str
    """Title"""


@dataclass
class JikanPropStruct:
    """Jikan Date Property Struct"""

    day: int | None = None
    """Day of the month"""
    month: int | None = None
    """Month of the year"""
    year: int | None = None
    """Year"""


@dataclass
class JikanPropParentStruct:
    """Jikan Date Property Parent Struct"""

    from_: JikanPropStruct | None = None
    """Properties of the start date"""
    # pylint: disable-next=invalid-name
    to: JikanPropStruct | None = None
    """Properties of the end date"""


@dataclass
class JikanDateStruct:
    """Jikan Date Struct"""

    from_: datetime | None = None
    """Start date"""
    # pylint: disable-next=invalid-name
    to: datetime | None = None
    """End date"""
    prop: JikanPropParentStruct | None = None
    """Properties of the date"""
    string: str | None = None
    """Date as a string"""


@dataclass
class JikanBroadcastStruct:
    """Jikan Broadcast Struct"""

    day: (
        Literal[
            "Mondays",
            "Tuesdays",
            "Wednesdays",
            "Thursdays",
            "Fridays",
            "Saturdays",
            "Sundays",
        ]
        | None
    ) = None
    """Day of the week"""
    time: str | None = None
    """Time of the day"""
    timezone: str | None = None
    """Timezone"""
    string: str | None = None
    """Broadcast as a string"""


@dataclass
class JikanOtherStruct:
    """Jikan Other Struct"""

    mal_id: int
    """MyAnimeList ID"""
    type: str
    """Type of the entry"""
    name: str
    """Name of the entry"""
    url: str
    """URL of the entry"""


@dataclass
class JikanRelationStruct:
    """Jikan Relation Struct"""

    relation: str
    """Relation between the entries"""
    entry: list[JikanOtherStruct]
    """Entry"""


@dataclass
class JikanThemeSongStruct:
    """Jikan Theme Song Struct"""

    openings: list[str] | None = None
    """List of opening songs"""
    endings: list[str] | None = None
    """List of ending songs"""


@dataclass
class JikanExternalStruct:
    """Jikan External Struct"""

    name: str
    """Name of the external site"""
    url: str
    """URL of the external site"""


@dataclass
class JikanAnimeStruct:
    """Jikan Anime Struct"""

    mal_id: int
    """MyAnimeList ID"""
    url: str
    """URL of the anime"""
    images: JikanImages | None
    """Images of the anime"""
    trailer: JikanTrailerStruct | list[JikanTrailerStruct] | None
    """Trailer of the anime"""
    approved: bool
    """Whether the anime is approved"""
    titles: list[JikanTitlesStruct] | None
    """Titles of the anime"""
    title: str
    """Title of the anime"""
    type: Literal["TV", "OVA", "Movie", "Special", "ONA", "Music", "Unknown"] | None
    """Type of the anime"""
    source: (
        Literal[
            "Original",
            "Manga",
            "Light novel",
            "Visual novel",
            "Video game",
            "Other",
            "Novel",
            "Doujinshi",
            "Anime",
            "Web manga",
            "Unknown",
        ]
        | None
    )
    """Source of the anime"""
    episodes: int | None
    """Number of episodes"""
    status: Literal["Currently Airing", "Finished Airing", "Not yet aired"] | None
    """Status of the anime"""
    airing: bool | None
    """Whether the anime is airing"""
    aired: JikanDateStruct | None
    """Airing dates of the anime"""
    duration: str | None
    """Duration of the anime"""
    rating: (
        Literal[
            "G - All Ages",
            "PG - Children",
            "PG-13 - Teens 13 or older",
            "R - 17+ (violence & profanity)",
            "R+ - Mild Nudity",
            "Rx - Hentai",
        ]
        | None
    )
    """Content/age rating of the anime"""
    score: float | None
    """Score of the anime"""
    scored_by: int | None
    """Number of people who scored the anime"""
    rank: int | None
    """Rank of the anime"""
    popularity: int | None
    """Popularity of the anime"""
    members: int | None
    """Number of members"""
    favorites: int | None
    """Number of favorites"""
    synopsis: str | None
    """Synopsis of the anime"""
    background: str | None
    """Background information of the anime"""
    season: Literal["winter", "spring", "summer", "fall"] | None
    """Season of the anime"""
    year: int | None
    """Release year of the anime"""
    broadcast: JikanBroadcastStruct | None
    """Broadcast information"""
    producers: list[JikanOtherStruct] | None
    """List of producers"""
    licensors: list[JikanOtherStruct] | None
    """List of licensors"""
    studios: list[JikanOtherStruct] | None
    """List of studios"""
    genres: list[JikanOtherStruct] | None
    """List of genres"""
    explicit_genres: list[JikanOtherStruct] | None
    """List of explicit genres"""
    themes: list[JikanOtherStruct] | None
    """List of themes"""
    demographics: list[JikanOtherStruct] | None
    """List of demographics"""
    title_english: str | None = None
    """English title"""
    title_japanese: str | None = None
    """Japanese title"""
    title_synonyms: list[str] | None = None
    """List of synonyms"""
    relations: list[JikanRelationStruct] | None = None
    """List of relations"""
    theme: list[JikanThemeSongStruct] | None = None
    """List of theme songs"""
    external: list[JikanExternalStruct] | None = None
    """List of external sites"""
    streaming: list[JikanExternalStruct] | None = None
    """List of streaming sites"""


@dataclass
class JikanStatisticsStruct:
    """Jikan Statistics Struct"""

    mean_score: float | None
    """Mean score"""
    completed: int | None
    """Number of completed entries"""
    on_hold: int | None
    """Number of entries on hold"""
    dropped: int | None
    """Number of dropped entries"""
    total_entries: int | None
    """Total number of entries listed"""


@dataclass
class JikanAnimeStatisticStruct(JikanStatisticsStruct):
    """Jikan Anime Statistics Struct"""

    days_watched: float | None
    """Number of days watched"""
    watching: int | None
    """Number of entries being watched"""
    plan_to_watch: int | None
    """Number of entries planned to watch"""
    rewatched: int | None
    """Number of rewatched entries"""
    episodes_watched: int | None
    """Number of episodes watched"""


@dataclass
class JikanMangaStatisticStruct(JikanStatisticsStruct):
    """Jikan Manga Statistics Struct"""

    days_read: float | None
    """Number of (estimated) days read"""
    reading: int | None
    """Number of entries being read"""
    plan_to_read: int | None
    """Number of entries planned to read"""
    reread: int | None
    """Number of reread entries"""
    chapters_read: int | None
    """Number of chapters read"""
    volumes_read: int | None
    """Number of volumes read"""


@dataclass
class JikanStatistics:
    """Jikan Statistics"""

    anime: JikanAnimeStatisticStruct | None
    """Anime statistics"""
    manga: JikanMangaStatisticStruct | None
    """Manga statistics"""


@dataclass
class JikanUserTitleStruct:
    """Jikan User Title Struct"""

    mal_id: int
    """MyAnimeList ID"""
    url: str
    """URL of the entry"""
    images: JikanImages | None
    """Images of the entry"""


@dataclass
class JikanUserAniMangaStruct(JikanUserTitleStruct):
    """Jikan User Anime/Manga Struct"""

    title: str
    """Title of the entry"""
    type: str | None = None
    """Type of the entry"""
    start_year: int | None = None
    """Start year of the entry"""


@dataclass
class JikanUserCastStruct(JikanUserTitleStruct):
    """Jikan User Cast Struct"""

    name: str | None
    """Name of the person/character"""


@dataclass
class JikanUpdateEntry:
    """Jikan Update Entry"""

    entry: JikanUserAniMangaStruct
    """Entry that was updated"""
    score: int | None = None
    """Score given to the entry"""
    status: str | None = None
    """Status of the entry"""
    date: datetime | None = None
    """Date of the update"""


@dataclass
class JikanAnimeUpdateEntry(JikanUpdateEntry):
    """Jikan Anime Update Entry"""

    episodes_seen: int | None = None
    """Number of episodes seen"""
    episodes_total: int | None = None
    """Total number of episodes"""


@dataclass
class JikanMangaUpdateEntry(JikanUpdateEntry):
    """Jikan Manga Update Entry"""

    chapters_read: int | None = None
    """Number of chapters read"""
    chapters_total: int | None = None
    """Total number of chapters"""


@dataclass
class JikanUserFavorite:
    """Jikan User Favorite"""

    anime: list[JikanUserAniMangaStruct] | None = None
    """List of favorite anime"""
    manga: list[JikanUserAniMangaStruct] | None = None
    """List of favorite manga"""
    characters: list[JikanUserCastStruct] | None = None
    """List of favorite characters"""
    people: list[JikanUserCastStruct] | None = None
    """List of favorite people"""


@dataclass
class JikanUserStatus:
    """Jikan User Status"""

    anime: list[JikanAnimeUpdateEntry] | None = None
    """List of anime updates"""
    manga: list[JikanMangaUpdateEntry] | None = None
    """List of manga updates"""


@dataclass
class JikanUserStruct:
    """Jikan User Struct"""

    mal_id: int
    """MyAnimeList ID"""
    username: str
    """Username"""
    url: str
    """URL of the user"""
    joined: datetime
    """Date the user joined MyAnimeList"""
    images: JikanImages | None = None
    """Images of the user"""
    location: str | None = None
    """Location of the user"""
    gender: str | None = None
    """Gender of the user"""
    last_online: datetime | None = None
    """Date the user was last online"""
    birthday: datetime | None = None
    """Date of birth of the user"""
    statistics: JikanStatistics | None = None
    """Statistics of the user"""
    favorites: JikanUserFavorite | None = None
    """Favorites of the user"""
    updates: JikanUserStatus | None = None
    """Updates of the user"""
    about: str | None = None
    """About of the user"""
    external: dict[str, Any] | list[dict[str, Any] | str] | None = None
    """External links of the user"""


def define_jikan_exception(error_code: int, error_message: Any) -> None:
    """
    Define Jikan Exception

    Args:
        error_code (int): Error code
        error_message (Any): Error message

    Raises:
        JikanException: Jikan Exception

    Returns:
        None: Action acknowledge
    """
    try:
        match error_code:
            case 403:
                err_ = "**Jikan unable to reach MyAnimeList at the moment**\nPlease try again in 3 seconds."
            case 404:
                err_ = "**I couldn't find the query on MAL**\nCheck the spelling or well, maybe they don't exist? 🤔"
            case 408:
                err_ = "**Jikan had a timeout while fetching the data**\nPlease try again in 3 seconds."
            case 418:
                err_ = f"""**It seems that I can't parse the response from Jikan due to missing data, ouch**
Please contact Ryuusei's dev team to resolve this issue
Full message:```
{error_message}
```"""
            case 429:
                err_ = "**I have been rate-limited by Jikan**\nAny queries related to MyAnimeList may not available "
            case 500:
                err_ = "**Uh, it seems Jikan had a bad day, and this specific endpoint might broken**\nYou could help dev team to resolve this issue"
                if isinstance(error_message, dict) and "report_url" in error_message:
                    err_ += f" by clicking [this link to directly submit a GitHub Issue]({error_message['report_url']})"
                else:
                    err_ += f"\nFull message:\n{error_message}"
            case 503:
                err_ = "**I think Jikan is dead, server can't be reached** :/"
            case _:
                err_ = f"HTTP error code: {error_code}\n{error_message}"
    # pylint: disable-next=broad-except
    except Exception:  # noqa: BLE001
        err_ = "Unknown error. Full traceback:\n" + traceback.format_exc()

    raise JikanException(err_, error_code)


class JikanApi:
    """Jikan API wrapper"""

    def __init__(self, base_url: str = JIKAN_URL):
        """
        Init

        Args:
            base_url (str, optional): Jikan-compatible API base URL.
                Defaults to JIKAN_URL.
        """
        self.base_url = base_url.rstrip("/")
        self.session = None

    async def __aenter__(self):
        """Enter the session"""
        self.session = ClientSession(headers={"User-Agent": USER_AGENT})
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the session"""
        await self.close()

    async def close(self):
        """Close the session"""
        if self.session is not None:
            await self.session.close()
            self.session = None

    async def _request_json(
        self, path: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        GET a JSON envelope, mapping HTTP failures to JikanException.

        Args:
            path (str): URL path starting with "/"
            params (dict[str, Any] | None, optional): Query parameters

        Raises:
            JikanException: When the endpoint answers with an error status
                or an unparsable body

        Returns:
            dict[str, Any]: The decoded response envelope
        """
        async with self.session.get(
            f"{self.base_url}{path}", params=params, timeout=REQUEST_TIMEOUT
        ) as resp:
            try:
                body = await resp.json()
            except Exception:  # noqa: BLE001
                body = None
            if resp.status not in (200, 304) or not isinstance(body, dict):
                if isinstance(body, dict):
                    define_jikan_exception(
                        body.get("status", resp.status),
                        body.get("message", resp.reason),
                    )
                define_jikan_exception(resp.status, resp.reason)
            return body

    @staticmethod
    def _parse_dt(value: Any) -> datetime | None:
        """
        Parse a Jikan datetime string, tolerating format variance.

        Args:
            value (Any): The raw value

        Returns:
            datetime | None: The parsed datetime or None when unparsable
        """
        if not isinstance(value, str) or not value:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S%z")
        except ValueError:
            pass
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None

    @staticmethod
    def _field_names(klass: type) -> set[str]:
        """
        Dataclass field names of a struct.

        Args:
            klass (type): The dataclass

        Returns:
            set[str]: Field names, used to drop unknown API keys
        """
        return {field.name for field in fields(klass)}

    @classmethod
    def _build(cls, klass: type, data: Any) -> Any:
        """
        Build a struct from a mapping, dropping unknown keys.

        Args:
            klass (type): The dataclass to build
            data (Any): The raw mapping

        Returns:
            Any: The struct, or None when data is not a mapping
        """
        if not isinstance(data, dict):
            return None
        known = cls._field_names(klass)
        return klass(**{key: data[key] for key in data if key in known})

    @classmethod
    def _convert_image(cls, data: Any) -> JikanImageStruct | None:
        """
        Convert an image entry, tolerating missing variants.

        Args:
            data (Any): The raw image entry

        Returns:
            JikanImageStruct | None: The struct or None
        """
        if not isinstance(data, dict):
            return None
        return JikanImageStruct(
            image_url=data.get("image_url") or "",
            small_image_url=data.get("small_image_url"),
            large_image_url=data.get("large_image_url"),
            medium_image_url=data.get("medium_image_url"),
            maximum_image_url=data.get("maximum_image_url"),
        )

    @classmethod
    def _convert_images(cls, data: Any) -> JikanImages | None:
        """
        Convert an images block, tolerating missing variants.

        Args:
            data (Any): The raw images block

        Returns:
            JikanImages | None: The struct or None
        """
        if not isinstance(data, dict):
            return None
        jpg = cls._convert_image(data.get("jpg"))
        webp = cls._convert_image(data.get("webp"))
        if jpg is None and webp is None:
            return None
        return JikanImages(jpg=jpg, webp=webp)

    @classmethod
    def _convert_trailer(cls, data: Any) -> JikanTrailerStruct | None:
        """
        Convert a trailer entry.

        Args:
            data (Any): The raw trailer entry

        Returns:
            JikanTrailerStruct | None: The struct or None
        """
        if not isinstance(data, dict):
            return None
        return JikanTrailerStruct(
            youtube_id=data.get("youtube_id") or "",
            url=data.get("url") or "",
            embed_url=data.get("embed_url") or "",
            images=cls._convert_images(data.get("images")),
        )

    @classmethod
    def _convert_titles(cls, data: Any) -> list[JikanTitlesStruct] | None:
        """
        Convert title entries, skipping malformed ones.

        Args:
            data (Any): The raw titles list

        Returns:
            list[JikanTitlesStruct] | None: The structs or None
        """
        if not isinstance(data, list):
            return None
        titles = [
            JikanTitlesStruct(type=title.get("type"), title=title.get("title") or "")
            for title in data
            if isinstance(title, dict)
        ]
        return titles or None

    @staticmethod
    def _convert_prop(data: Any) -> JikanPropStruct:
        """
        Convert a date property entry.

        Args:
            data (Any): The raw property entry

        Returns:
            JikanPropStruct: The struct (all None when missing)
        """
        if not isinstance(data, dict):
            data = {}
        return JikanPropStruct(
            day=data.get("day"), month=data.get("month"), year=data.get("year")
        )

    @classmethod
    def _convert_aired(cls, data: Any) -> JikanDateStruct | None:
        """
        Convert an aired block without mutating the input.

        Args:
            data (Any): The raw aired block

        Returns:
            JikanDateStruct | None: The struct or None
        """
        if not isinstance(data, dict):
            return None
        prop = data.get("prop") or {}
        return JikanDateStruct(
            from_=cls._parse_dt(data.get("from")),
            to=cls._parse_dt(data.get("to")),
            prop=JikanPropParentStruct(
                from_=cls._convert_prop(prop.get("from")),
                to=cls._convert_prop(prop.get("to")),
            ),
            string=data.get("string"),
        )

    @classmethod
    def _convert_broadcast(cls, data: Any) -> JikanBroadcastStruct | None:
        """
        Convert a broadcast block.

        Args:
            data (Any): The raw broadcast block

        Returns:
            JikanBroadcastStruct | None: The struct or None
        """
        if not isinstance(data, dict):
            return None
        return JikanBroadcastStruct(
            day=data.get("day"),
            time=data.get("time"),
            timezone=data.get("timezone"),
            string=data.get("string"),
        )

    @staticmethod
    def _convert_other(data: Any) -> JikanOtherStruct | None:
        """
        Convert an ID/name reference entry.

        Args:
            data (Any): The raw entry

        Returns:
            JikanOtherStruct | None: The struct or None when not a mapping
        """
        if not isinstance(data, dict):
            return None
        return JikanOtherStruct(
            mal_id=data.get("mal_id"),
            type=data.get("type") or "",
            name=data.get("name") or "",
            url=data.get("url") or "",
        )

    @classmethod
    def _convert_others(cls, data: Any) -> list[JikanOtherStruct] | None:
        """
        Convert a list of reference entries, skipping malformed ones.

        Args:
            data (Any): The raw list

        Returns:
            list[JikanOtherStruct] | None: The structs or None
        """
        if not isinstance(data, list):
            return None
        items = [cls._convert_other(entry) for entry in data]
        items = [entry for entry in items if entry is not None]
        return items or None

    @classmethod
    def anime_dict_to_dataclass(cls, data: dict) -> JikanAnimeStruct:
        """
        Convert anime dict to dataclass without mutating the input.

        Unknown keys are dropped so endpoint variance cannot break parsing.

        Args:
            data (dict): Anime dict

        Returns:
            JikanAnimeStruct: Anime dataclass
        """
        payload = dict(data) if isinstance(data, dict) else {}
        payload["images"] = cls._convert_images(payload.get("images"))
        payload["trailer"] = cls._convert_trailer(payload.get("trailer"))
        payload["titles"] = cls._convert_titles(payload.get("titles"))
        payload["aired"] = cls._convert_aired(payload.get("aired"))
        payload["broadcast"] = cls._convert_broadcast(payload.get("broadcast"))
        for key in (
            "producers",
            "licensors",
            "studios",
            "genres",
            "explicit_genres",
            "themes",
            "demographics",
        ):
            payload[key] = cls._convert_others(payload.get(key))
        relations = payload.get("relations")
        if isinstance(relations, list):
            converted = []
            for rel in relations:
                if not isinstance(rel, dict):
                    continue
                entries = cls._convert_others(rel.get("entry")) or []
                converted.append(
                    JikanRelationStruct(
                        relation=rel.get("relation") or "", entry=entries
                    )
                )
            payload["relations"] = converted or None
        else:
            payload["relations"] = None
        theme = payload.get("theme")
        payload["theme"] = cls._build(JikanThemeSongStruct, theme)
        payload["external"] = cls._convert_externals(payload.get("external"))
        payload["streaming"] = cls._convert_externals(payload.get("streaming"))
        return cls._build(JikanAnimeStruct, payload)

    @classmethod
    def _convert_externals(cls, data: Any) -> list[JikanExternalStruct] | None:
        """
        Convert external/streaming entries, skipping unusable ones.

        Args:
            data (Any): The raw list

        Returns:
            list[JikanExternalStruct] | None: The structs or None
        """
        if not isinstance(data, list):
            return None
        entries = [cls._build(JikanExternalStruct, item) for item in data]
        entries = [
            entry for entry in entries if entry is not None and entry.name and entry.url
        ]
        return entries or None

    @classmethod
    def _convert_user_title(cls, data: Any, klass: type) -> Any:
        """
        Convert a user favorites/updates title entry.

        Args:
            data (Any): The raw entry
            klass (type): The struct to build

        Returns:
            Any: The struct or None when unusable
        """
        if not isinstance(data, dict):
            return None
        payload = {
            key: data[key]
            for key in data
            if key in cls._field_names(klass) and key != "images"
        }
        payload["images"] = cls._convert_images(data.get("images"))
        try:
            return klass(**payload)
        except TypeError:
            return None

    @classmethod
    def _convert_user_titles(cls, data: Any, klass: type) -> list | None:
        """
        Convert a list of user title entries, skipping malformed ones.

        Args:
            data (Any): The raw list
            klass (type): The struct to build per entry

        Returns:
            list | None: The structs or None
        """
        if not isinstance(data, list):
            return None
        items = [cls._convert_user_title(entry, klass) for entry in data]
        items = [entry for entry in items if entry is not None]
        return items or None

    @classmethod
    def _convert_user_updates(cls, data: Any, klass: type) -> list | None:
        """
        Convert a list of user update entries, skipping malformed ones.

        Args:
            data (Any): The raw list
            klass (type): The update struct to build per entry

        Returns:
            list | None: The structs or None
        """
        if not isinstance(data, list):
            return None
        items = []
        for update in data:
            if not isinstance(update, dict):
                continue
            entry = cls._convert_user_title(
                update.get("entry"), JikanUserAniMangaStruct
            )
            if entry is None:
                continue
            payload = {
                key: update[key]
                for key in update
                if key in cls._field_names(klass) and key != "entry"
            }
            payload["entry"] = entry
            payload["date"] = cls._parse_dt(update.get("date"))
            try:
                items.append(klass(**payload))
            except TypeError:
                continue
        return items or None

    @classmethod
    def _convert_user_statistics(cls, data: Any) -> JikanStatistics | None:
        """
        Convert a user statistics block.

        Args:
            data (Any): The raw block

        Returns:
            JikanStatistics | None: The struct or None
        """
        if not isinstance(data, dict):
            return None
        return JikanStatistics(
            anime=cls._build(JikanAnimeStatisticStruct, data.get("anime")),
            manga=cls._build(JikanMangaStatisticStruct, data.get("manga")),
        )

    @classmethod
    def _convert_user_favorites(cls, data: Any) -> JikanUserFavorite | None:
        """
        Convert a user favorites block.

        Args:
            data (Any): The raw block

        Returns:
            JikanUserFavorite | None: The struct or None
        """
        if not isinstance(data, dict):
            return None
        return JikanUserFavorite(
            anime=cls._convert_user_titles(data.get("anime"), JikanUserAniMangaStruct),
            manga=cls._convert_user_titles(data.get("manga"), JikanUserAniMangaStruct),
            characters=cls._convert_user_titles(
                data.get("characters"), JikanUserCastStruct
            ),
            people=cls._convert_user_titles(data.get("people"), JikanUserCastStruct),
        )

    @classmethod
    def _convert_user_status(cls, data: Any) -> JikanUserStatus | None:
        """
        Convert a user updates block.

        Args:
            data (Any): The raw block

        Returns:
            JikanUserStatus | None: The struct or None
        """
        if not isinstance(data, dict):
            return None
        return JikanUserStatus(
            anime=cls._convert_user_updates(data.get("anime"), JikanAnimeUpdateEntry),
            manga=cls._convert_user_updates(data.get("manga"), JikanMangaUpdateEntry),
        )

    @classmethod
    def user_dict_to_dataclass(cls, data: dict) -> JikanUserStruct:
        """
        Convert user dict to dataclass without mutating the input.

        Unknown keys are dropped and malformed entries skipped so endpoint
        variance cannot break parsing.

        Args:
            data (dict): User dict

        Returns:
            JikanUserStruct: User dataclass
        """
        payload = dict(data) if isinstance(data, dict) else {}
        payload["images"] = cls._convert_images(payload.get("images"))
        payload["last_online"] = cls._parse_dt(payload.get("last_online"))
        payload["birthday"] = cls._parse_dt(payload.get("birthday"))
        payload["joined"] = cls._parse_dt(payload.get("joined"))
        payload["statistics"] = cls._convert_user_statistics(payload.get("statistics"))
        payload["favorites"] = cls._convert_user_favorites(payload.get("favorites"))
        payload["updates"] = cls._convert_user_status(payload.get("updates"))
        return cls._build(JikanUserStruct, payload)

    async def get_user_clubs(self, username: str) -> list[dict]:
        """
        Get user joined clubs

        Args:
            username (str): MyAnimeList username

        Returns:
            list[dict]: List of clubs
        """
        try:
            resp_data = await self._request_json(f"/users/{username}/clubs")
            clubs: list = resp_data.get("data") or []
            paging: int = (resp_data.get("pagination") or {}).get(
                "last_visible_page", 1
            )
            if paging > 1:
                for i in range(2, paging + 1):
                    page_data = await self._request_json(
                        f"/users/{username}/clubs", params={"page": i}
                    )
                    clubs.extend(page_data.get("data") or [])
                    await asyncio.sleep(2)
            return clubs
        # pylint: disable-next=broad-except
        except Exception as error:
            if isinstance(error, JikanException):
                raise
            define_jikan_exception(601, error)

    async def get_user_data(self, username: str) -> JikanUserStruct:
        """
        Get user data

        Args:
            username (str): MyAnimeList username

        Actions:
            If Jikan took too long to respond, it will try again in multiples of 3 seconds for exponential backoff

        Returns:
            dict: User data
        """
        cache_file_path = Cache.get_cache_file_path(f"user/{username}.json")
        cached_file = Cache.read_cached_data(cache_file_path, 43200)
        if cached_file:
            return self.user_dict_to_dataclass(cached_file)

        last_error: Exception | None = None
        for attempt in range(3):
            try:
                body = await self._request_json(f"/users/{username}/full")
                res = body.get("data")
                if not isinstance(res, dict):
                    raise JikanException("Unexpected user payload", 418)
                try:
                    user = self.user_dict_to_dataclass(res)
                except Exception as error:  # noqa: BLE001
                    define_jikan_exception(418, error)
                Cache.write_data_to_cache(res, cache_file_path)
                return user
            except JikanException as error:
                if error.status_code not in _RETRYABLE_STATUS:
                    raise
                last_error = error
            except (asyncio.TimeoutError, ClientError) as error:
                last_error = error
            if attempt < 2:
                await asyncio.sleep(3 ** (attempt + 1))
        if isinstance(last_error, JikanException):
            raise last_error
        define_jikan_exception(601, last_error)

    async def get_user_by_id(self, user_id: int) -> JikanUserStruct:
        """
        Get user data from their MAL ID

        Args:
            user_id (int): MyAnimeList user ID

        Actions:
            If Jikan took too long to respond, it will try again in multiples of 3 seconds for exponential backoff

        Returns:
            JikanUserStruct: User data
        """
        async with self.session.get(
            f"{self.base_url}/users/userbyid/{user_id}", timeout=REQUEST_TIMEOUT
        ) as resp:
            if resp.status in [200, 304]:
                try:
                    res = await resp.json()
                except Exception:  # noqa: BLE001
                    res = None
                username = (
                    (res.get("data") or {}).get("username")
                    if isinstance(res, dict)
                    else None
                )
                if not username:
                    raise ProviderHttpError("Unexpected userbyid payload", resp.status)
            else:
                try:
                    data = await resp.json()
                except Exception:  # noqa: BLE001
                    data = resp.reason
                raise ProviderHttpError(str(data), resp.status)
        gud = await self.get_user_data(username)
        return gud

    async def get_anime_data(self, anime_id: int) -> JikanAnimeStruct:
        """
        Get anime data

        Args:
            anime_id (int): MyAnimeList anime ID

        Returns:
            dict: Anime data
        """
        cache_file_path = Cache.get_cache_file_path(f"anime/{anime_id}.json")
        cached_file = Cache.read_cached_data(cache_file_path)
        if cached_file:
            return self.anime_dict_to_dataclass(cached_file)
        try:
            body = await self._request_json(f"/anime/{anime_id}/full")
            res = body.get("data")
            if not isinstance(res, dict):
                raise JikanException("Unexpected anime payload", 418)
            anime = self.anime_dict_to_dataclass(res)
            Cache.write_data_to_cache(res, cache_file_path)
            return anime
        # pylint: disable-next=broad-except
        except Exception as error:
            if isinstance(error, JikanException):
                raise
            define_jikan_exception(418, error)
