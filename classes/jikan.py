"""Jikan API Wrapper"""

import asyncio
import traceback
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal

from aiohttp import ClientSession

from classes.cache import Caching
from modules.const import USER_AGENT

Cache = Caching(cache_directory="cache/jikan", cache_expiration_time=86400)


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

    type: Literal[
        "Default",
        "Synonym",
        "English",
        "Japanese",
        "Synonym",
        "German",
        "Spanish",
        "Italian",
        "French",
        "Korean",
        "Portuguese",
        "Chinese",
        "Korean",
    ] | None
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

    day: Literal[
        "Mondays",
        "Tuesdays",
        "Wednesdays",
        "Thursdays",
        "Fridays",
        "Saturdays",
        "Sundays",
    ] | None = None
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
    type: Literal["TV", "OVA", "Movie", "Special",
                  "ONA", "Music", "Unknown"] | None
    """Type of the anime"""
    source: Literal[
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
    ] | None
    """Source of the anime"""
    episodes: int | None
    """Number of episodes"""
    status: Literal["Airing", "Finished Airing", "Not yet aired"] | None
    """Status of the anime"""
    airing: bool | None
    """Whether the anime is airing"""
    aired: JikanDateStruct | None
    """Airing dates of the anime"""
    duration: str | None
    """Duration of the anime"""
    rating: Literal[
        "G - All Ages",
        "PG - Children",
        "PG-13 - Teens 13 or older",
        "R - 17+ (violence & profanity)",
        "R+ - Mild Nudity",
        "Rx - Hentai",
    ] | None
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
    images: JikanImages | None
    """Images of the user"""
    location: str | None
    """Location of the user"""
    joined: datetime
    """Date the user joined MyAnimeList"""
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
                if isinstance(error_message,
                              dict) and "report_url" in error_message:
                    err_ += f" by clicking [this link to directly submit a GitHub Issue]({error_message['report_url']})"
                else:
                    err_ += f"\nFull message:\n{error_message}"
            case 503:
                err_ = "**I think Jikan is dead, server can't be reached** :/"
            case _:
                err_ = f"HTTP error code: {error_code}\n{error_message}"
    # pylint: disable-next=broad-except
    except Exception:
        err_ = "Unknown error. Full traceback:\n" + traceback.format_exc()

    raise JikanException(err_, error_code)


class JikanApi:
    """Jikan API wrapper"""

    def __init__(self):
        """Init"""
        self.base_url = "https://api.jikan.moe/v4"
        self.session = None
        self.user_agent = ""

    async def __aenter__(self):
        """Enter the session"""
        self.session = ClientSession(headers={"User-Agent": USER_AGENT})
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the session"""
        await self.close()

    async def close(self):
        """Close the session"""
        await self.session.close()

    @staticmethod
    def anime_dict_to_dataclass(data: dict) -> JikanAnimeStruct:
        """
        Convert anime dict to dataclass

        Args:
            data (dict): Anime dict

        Returns:
            JikanAnimeStruct: Anime dataclass
        """
        if data.get("images", None):
            data["images"]["jpg"] = JikanImageStruct(**data["images"]["jpg"])
            data["images"]["webp"] = JikanImageStruct(**data["images"]["webp"])
            data["images"] = JikanImages(**data["images"])

        if data.get("trailer", None):
            data["trailer"]["images"] = JikanImageStruct(
                **data["trailer"]["images"])
            data["trailer"] = JikanTrailerStruct(**data["trailer"])

        if data.get("titles", None):
            data["titles"] = [
                JikanTitlesStruct(
                    type=title["type"],
                    title=title["title"],
                )
                for title in data["titles"]
            ]

        if data.get("aired", None):
            data["aired"]["prop"]["from_"] = data["aired"]["prop"]["from"]
            data["aired"]["prop"]["from_"] = JikanPropStruct(
                **data["aired"]["prop"]["from_"]
            )
            del data["aired"]["prop"]["from"]
            data["aired"]["prop"]["to"] = data["aired"]["prop"]["to"]
            data["aired"]["prop"]["to"] = JikanPropStruct(
                **data["aired"]["prop"]["to"])
            data["aired"]["prop"] = JikanPropParentStruct(
                **data["aired"]["prop"])
            if data["aired"].get("from", None):
                data["aired"]["from_"] = datetime.strptime(
                    data["aired"]["from"], "%Y-%m-%dT%H:%M:%S%z"
                )
            del data["aired"]["from"]
            if data["aired"].get("to", None):
                data["aired"]["to"] = datetime.strptime(
                    data["aired"]["to"], "%Y-%m-%dT%H:%M:%S%z"
                )
            data["aired"] = JikanDateStruct(**data["aired"])

        if data.get("broadcast", None):
            data["broadcast"] = JikanBroadcastStruct(**data["broadcast"])

        if data.get("producers", None):
            data["producers"] = [
                JikanOtherStruct(
                    mal_id=producer["mal_id"],
                    type=producer["type"],
                    name=producer["name"],
                    url=producer["url"],
                )
                for producer in data["producers"]
            ]
        if data.get("licensors", None):
            data["licensors"] = [
                JikanOtherStruct(
                    mal_id=licensor["mal_id"],
                    type=licensor["type"],
                    name=licensor["name"],
                    url=licensor["url"],
                )
                for licensor in data["licensors"]
            ]
        if data.get("studios", None):
            data["studios"] = [
                JikanOtherStruct(
                    mal_id=studio["mal_id"],
                    type=studio["type"],
                    name=studio["name"],
                    url=studio["url"],
                )
                for studio in data["studios"]
            ]
        if data.get("genres", None):
            data["genres"] = [
                JikanOtherStruct(
                    mal_id=genre["mal_id"],
                    type=genre["type"],
                    name=genre["name"],
                    url=genre["url"],
                )
                for genre in data["genres"]
            ]
        if data.get("explicit_genres", None):
            data["explicit_genres"] = [
                JikanOtherStruct(
                    mal_id=genre["mal_id"],
                    type=genre["type"],
                    name=genre["name"],
                    url=genre["url"],
                )
                for genre in data["explicit_genres"]
            ]
        if data.get("themes", None):
            data["themes"] = [
                JikanOtherStruct(
                    mal_id=theme["mal_id"],
                    type=theme["type"],
                    name=theme["name"],
                    url=theme["url"],
                )
                for theme in data["themes"]
            ]
        if data.get("demographics", None):
            data["demographics"] = [
                JikanOtherStruct(
                    mal_id=demographic["mal_id"],
                    type=demographic["type"],
                    name=demographic["name"],
                    url=demographic["url"],
                )
                for demographic in data["demographics"]
            ]

        if data.get("relations", None):
            data["relations"] = [
                JikanRelationStruct(
                    relation=rel["relation"],
                    entry=[
                        JikanOtherStruct(
                            mal_id=entry["mal_id"],
                            type=entry["type"],
                            name=entry["name"],
                            url=entry["url"],
                        )
                        for entry in rel["entry"]
                    ],
                )
                for rel in data["relations"]
            ]

        if data.get("theme", None):
            data["theme"] = JikanThemeSongStruct(**data["theme"])

        if data.get("external", None):
            data["external"] = [
                JikanExternalStruct(
                    **external) for external in data["external"]]

        if data.get("streaming", None):
            data["streaming"] = [
                JikanExternalStruct(**stream) for stream in data["streaming"]
            ]

        return JikanAnimeStruct(**data)

    @staticmethod
    def user_dict_to_dataclass(data: dict) -> JikanUserStruct:
        """
        Convert user dict to dataclass

        Args:
            data (dict): User dict

        Returns:
            JikanUserStruct: User dataclass
        """
        if data["images"]:
            data["images"]["jpg"] = JikanImageStruct(**data["images"]["jpg"])
            data["images"]["webp"] = JikanImageStruct(**data["images"]["webp"])
            data["images"] = JikanImages(**data["images"])

        if data["last_online"]:
            data["last_online"] = datetime.strptime(
                data["last_online"], "%Y-%m-%dT%H:%M:%S%z"
            )

        if data["birthday"]:
            data["birthday"] = datetime.strptime(
                data["birthday"], "%Y-%m-%dT%H:%M:%S%z"
            )

        if data["joined"]:
            data["joined"] = datetime.strptime(
                data["joined"], "%Y-%m-%dT%H:%M:%S%z")

        if data["statistics"]:
            if data["statistics"]["anime"]:
                data["statistics"]["anime"] = JikanAnimeStatisticStruct(
                    **data["statistics"]["anime"]
                )
            if data["statistics"]["manga"]:
                data["statistics"]["manga"] = JikanMangaStatisticStruct(
                    **data["statistics"]["manga"]
                )
            data["statistics"] = JikanStatistics(**data["statistics"])

        if data["favorites"]:
            if data["favorites"]["anime"]:
                for anime in data["favorites"]["anime"]:
                    anime["images"]["jpg"] = JikanImageStruct(
                        **anime["images"]["jpg"])
                    anime["images"]["webp"] = JikanImageStruct(
                        **anime["images"]["webp"]
                    )
                    anime["images"] = JikanImages(**anime["images"])
                data["favorites"]["anime"] = [
                    JikanUserAniMangaStruct(**anime)
                    for anime in data["favorites"]["anime"]
                ]
            if data["favorites"]["manga"]:
                for manga in data["favorites"]["manga"]:
                    manga["images"]["jpg"] = JikanImageStruct(
                        **manga["images"]["jpg"])
                    manga["images"]["webp"] = JikanImageStruct(
                        **manga["images"]["webp"]
                    )
                    manga["images"] = JikanImages(**manga["images"])
                data["favorites"]["manga"] = [
                    JikanUserAniMangaStruct(**manga)
                    for manga in data["favorites"]["manga"]
                ]
            if data["favorites"]["characters"]:
                for character in data["favorites"]["characters"]:
                    character["images"]["jpg"] = JikanImageStruct(
                        **character["images"]["jpg"]
                    )
                    character["images"]["webp"] = JikanImageStruct(
                        **character["images"]["webp"]
                    )
                    character["images"] = JikanImages(**character["images"])
                data["favorites"]["characters"] = [
                    JikanUserCastStruct(**character)
                    for character in data["favorites"]["characters"]
                ]
            if data["favorites"]["people"]:
                for person in data["favorites"]["people"]:
                    person["images"]["jpg"] = JikanImageStruct(
                        **person["images"]["jpg"]
                    )
                    person["images"] = JikanImages(**person["images"])
                data["favorites"]["people"] = [
                    JikanUserCastStruct(**person)
                    for person in data["favorites"]["people"]
                ]
            data["favorites"] = JikanUserFavorite(**data["favorites"])

        if data["updates"]:
            if data["updates"]["anime"]:
                for anime in data["updates"]["anime"]:
                    anime["entry"]["images"]["jpg"] = JikanImageStruct(
                        **anime["entry"]["images"]["jpg"]
                    )
                    anime["entry"]["images"]["webp"] = JikanImageStruct(
                        **anime["entry"]["images"]["webp"]
                    )
                    anime["entry"]["images"] = JikanImages(
                        **anime["entry"]["images"])
                    anime["entry"] = JikanUserAniMangaStruct(**anime["entry"])
                    anime["date"] = datetime.strptime(
                        anime["date"], "%Y-%m-%dT%H:%M:%S%z"
                    )
                data["updates"]["anime"] = [JikanAnimeUpdateEntry(
                    **anime) for anime in data["updates"]["anime"]]
            if data["updates"]["manga"]:
                for manga in data["updates"]["manga"]:
                    manga["entry"]["images"]["jpg"] = JikanImageStruct(
                        **manga["entry"]["images"]["jpg"]
                    )
                    manga["entry"]["images"]["webp"] = JikanImageStruct(
                        **manga["entry"]["images"]["webp"]
                    )
                    manga["entry"]["images"] = JikanImages(
                        **manga["entry"]["images"])
                    manga["entry"] = JikanUserAniMangaStruct(**manga["entry"])
                    manga["date"] = datetime.strptime(
                        manga["date"], "%Y-%m-%dT%H:%M:%S%z"
                    )
                data["updates"]["manga"] = [JikanMangaUpdateEntry(
                    **manga) for manga in data["updates"]["manga"]]
            data["updates"] = JikanUserStatus(**data["updates"])

        return JikanUserStruct(**data)

    async def get_user_clubs(self, username: str) -> list[dict]:
        """
        Get user joined clubs

        Args:
            username (str): MyAnimeList username

        Returns:
            list[dict]: List of clubs
        """
        try:
            resp_data: dict = {}
            async with self.session.get(
                f"{self.base_url}/users/{username}/clubs"
            ) as resp:
                if resp.status in [200, 304]:
                    resp_data = await resp.json()
                else:
                    define_jikan_exception(resp.status, resp.reason)
            clubs: list = resp_data["data"]
            paging: int = resp_data["pagination"]["last_visible_page"]
            if paging > 1:
                for i in range(2, paging + 1):
                    params = {"page": i}
                    async with self.session.get(
                        f"{self.base_url}/users/{username}/clubs", params=params
                    ) as resp:
                        if resp.status in [200, 304]:
                            respd2: dict = await resp.json()
                            clubs.extend(respd2["data"])
                            await asyncio.sleep(2)
                        else:
                            define_jikan_exception(resp.status, resp.reason)
            return clubs
        # pylint: disable-next=broad-except
        except Exception as error:
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

        retries = 0
        res = {}
        while retries < 3:
            try:
                async with self.session.get(
                    f"{self.base_url}/users/{username}/full"
                ) as resp:
                    res = await resp.json()
                    status_code = res.get("status", 200)
                    if status_code != 200 or resp.status not in [200, 304]:
                        raise JikanException(
                            res.get("message", "Unknown error"), status_code
                        )
                    res: dict = res["data"]
                Cache.write_data_to_cache(res, cache_file_path)
                return self.user_dict_to_dataclass(res)
            except JikanException as error:
                retries += 1
                if retries == 3:
                    errcode: int = error.status_code if hasattr(
                        error, "status_code") else 418
                    errmsg: str | dict = error.message if hasattr(
                        error, "message") else error
                    define_jikan_exception(errcode, errmsg)
                else:
                    backoff_time = 3**retries
                    await asyncio.sleep(backoff_time)

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
            f"{self.base_url}/users/userbyid/{user_id}"
        ) as resp:
            if resp.status in [200, 304]:
                res = await resp.json()
                res: str = res["data"]["username"]
            else:
                # pylint: disable-next=broad-exception-raised
                raise Exception(await resp.json())
        gud = await self.get_user_data(res)
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
            async with self.session.get(
                f"{self.base_url}/anime/{anime_id}/full"
            ) as resp:
                res = await resp.json()
                status_code = res.get("status", 200)
                if status_code != 200 or resp.status not in [200, 304]:
                    raise JikanException(
                        res.get("message", "Unknown error"), status_code
                    )
                res: dict = res["data"]
            Cache.write_data_to_cache(res, cache_file_path)
            return self.anime_dict_to_dataclass(res)
        # pylint: disable-next=broad-except
        except Exception as error:
            errcode: int = error.status_code if hasattr(
                error, "status_code") else 418
            errmsg: str | dict = error.message if hasattr(
                error, "message") else error
            define_jikan_exception(errcode, errmsg)
