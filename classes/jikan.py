import asyncio
import json
import os
import time
import traceback
from typing import Any, Literal
from dataclasses import dataclass
from datetime import datetime

from aiohttp import ClientSession

from modules.const import USER_AGENT


class JikanException(Exception):
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code

    def __str__(self):
        return f"JikanException [{self.status_code}]: {self.message}"


@dataclass
class JikanImageStruct:
    image_url: str
    small_image_url: str | None = None
    large_image_url: str | None = None
    medium_image_url: str | None = None
    maximum_image_url: str | None = None


@dataclass
class JikanImages:
    jpg: JikanImageStruct | None = None
    webp: JikanImageStruct | None = None


@dataclass
class JikanTrailerStruct:
    youtube_id: str
    url: str
    embed_url: str
    images: JikanImages | None


@dataclass
class JikanTitlesStruct:
    type: str
    title: str


@dataclass
class JikanPropStruct:
    day: int
    month: int
    year: int


@dataclass
class JikanPropParentStruct:
    from_: JikanPropStruct | None = None
    to: JikanPropStruct | None = None


@dataclass
class JikanDateStruct:
    from_: datetime | None = None
    to: datetime | None = None
    prop: JikanPropParentStruct | None = None
    string: str | None = None


@dataclass
class JikanBroadcastStruct:
    day: Literal[
        "Mondays",
        "Tuesdays",
        "Wednesdays",
        "Thursdays",
        "Fridays",
        "Saturdays",
        "Sundays",
    ] | None = None
    time: str | None = None
    timezone: str | None = None
    string: str | None = None


@dataclass
class JikanOtherStruct:
    mal_id: int
    type: str
    name: str
    url: str


@dataclass
class JikanRelationStruct:
    relation: str
    entry: list[JikanOtherStruct]


@dataclass
class JikanThemeSongStruct:
    openings: list[str] | None = None
    endings: list[str] | None = None


@dataclass
class JikanExternalStruct:
    name: str
    url: str


@dataclass
class JikanAnimeStruct:
    mal_id: int
    url: str
    images: JikanImages | None
    trailer: JikanTrailerStruct | list[JikanTrailerStruct] | None
    approved: bool
    titles: list[JikanTitlesStruct] | None
    title: str
    type: str | None
    source: str | None
    episodes: int | None
    status: str | None
    airing: bool | None
    aired: JikanDateStruct | None
    duration: str | None
    rating: str | None
    score: float | None
    scored_by: int | None
    rank: int | None
    popularity: int | None
    members: int | None
    favorites: int | None
    synopsis: str | None
    background: str | None
    season: Literal["winter", "spring", "summer", "fall"] | None
    year: int | None
    broadcast: JikanBroadcastStruct | None
    producers: list[JikanOtherStruct] | None
    licensors: list[JikanOtherStruct] | None
    studios: list[JikanOtherStruct] | None
    genres: list[JikanOtherStruct] | None
    explicit_genres: list[JikanOtherStruct] | None
    themes: list[JikanOtherStruct] | None
    demographics: list[JikanOtherStruct] | None
    title_english: str | None = None
    title_japanese: str | None = None
    title_synonyms: list[str] | None = None
    relations: list[JikanRelationStruct] | None = None
    theme: list[JikanThemeSongStruct] | None = None
    external: list[JikanExternalStruct] | None = None
    streaming: list[JikanExternalStruct] | None = None


@dataclass
class JikanStatisticsStruct:
    mean_score: float | None
    completed: int | None
    on_hold: int | None
    dropped: int | None
    total_entries: int | None
    days_watched: int | None = None
    days_read: int | None = None
    watching: int | None = None
    reading: int | None = None
    plan_to_watch: int | None = None
    plan_to_read: int | None = None
    rewatched: int | None = None
    reread: int | None = None
    episodes_watched: int | None = None
    chapters_read: int | None = None
    volumes_read: int | None = None


@dataclass
class JikanStatistics:
    anime: JikanStatisticsStruct | None
    manga: JikanStatisticsStruct | None


@dataclass
class JikanUserTitleStruct:
    mal_id: int
    url: str
    images: JikanImages | None
    title: str | None = None  # for anime and manga
    name: str | None = None  # for characters, people
    type: str | None = None
    start_year: int | None = None


@dataclass
class JikanUpdateEntry:
    entry: JikanUserTitleStruct
    score: int | None = None
    status: str | None = None
    date: datetime | None = None
    episodes_seen: int | None = None
    episodes_total: int | None = None
    chapters_read: int | None = None
    chapters_total: int | None = None


@dataclass
class JikanUserFavorite:
    anime: list[JikanUserTitleStruct] | None = None
    manga: list[JikanUserTitleStruct] | None = None
    characters: list[JikanUserTitleStruct] | None = None
    people: list[JikanUserTitleStruct] | None = None


@dataclass
class JikanUserStatus:
    anime: list[JikanUpdateEntry] | None = None
    manga: list[JikanUpdateEntry] | None = None


@dataclass
class JikanUserStruct:
    mal_id: int
    username: str
    url: str
    images: JikanImages | None
    location: str | None
    joined: datetime
    gender: str | None = None
    last_online: datetime | None = None
    birthday: datetime | None = None
    statistics: JikanStatistics | None = None
    favorites: JikanUserFavorite | None = None
    updates: JikanUserStatus | None = None
    about: str | None = None
    external: dict[str, Any] | list[dict[str, Any] | str] | None = None


def defineJikanException(error_code: int, error_message: Any) -> JikanException:
    try:
        match error_code:
            case 403:
                em = "**Jikan unable to reach MyAnimeList at the moment**\nPlease try again in 3 seconds."
            case 404:
                em = "**I couldn't find the query on MAL**\nCheck the spelling or well, maybe they don't exist? 🤔"
            case 408:
                em = "**Jikan had a timeout while fetching the data**\nPlease try again in 3 seconds."
            case 429:
                em = "**I have been rate-limited by Jikan**\nAny queries related to MyAnimeList may not available "
            case 500:
                em = "**Uh, it seems Jikan had a bad day, and this specific endpoint might broken**\nYou could help dev team to resolve this issue"
                if isinstance(error_message, dict) and "report_url" in error_message:
                    em += f" by clicking [this link to directly submit a GitHub Issue]({error_message['report_url']})"
                else:
                    em += f"\nFull message:```\n{error_message}\n```"
            case 503:
                em = "**I think Jikan is dead, server can't be reached** :/"
            case _:
                em = f"HTTP error code: {error_code}\n```\n{error_message}\n```"
    except Exception:
        em = "Unknown error. Full traceback:\n" + traceback.format_exc()

    raise JikanException(em, error_code)


class JikanApi:
    """Jikan API wrapper"""

    def __init__(self):
        self.cache_directory = "cache/jikan"
        self.cache_expiration_time = 86400
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

    def anime_dict_to_dataclass(self, data: dict) -> JikanAnimeStruct:
        """Convert anime dict to dataclass

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
            data["trailer"]["images"] = JikanImageStruct(**data["trailer"]["images"])
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
            data["aired"]["prop"]["to"] = JikanPropStruct(**data["aired"]["prop"]["to"])
            data["aired"]["prop"] = JikanPropParentStruct(**data["aired"]["prop"])
            data["aired"]["from_"] = datetime.strptime(
                data["aired"]["from"], "%Y-%m-%dT%H:%M:%S%z"
            )
            data["aired"]["to"] = datetime.strptime(
                data["aired"]["to"], "%Y-%m-%dT%H:%M:%S%z"
            )
            del data["aired"]["from"]
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
                JikanExternalStruct(**external) for external in data["external"]
            ]

        if data.get("streaming", None):
            data["streaming"] = [
                JikanExternalStruct(**stream) for stream in data["streaming"]
            ]

        return JikanAnimeStruct(**data)

    def user_dict_to_dataclass(self, data: dict) -> JikanUserStruct:
        """Convert user dict to dataclass

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
            data["joined"] = datetime.strptime(data["joined"], "%Y-%m-%dT%H:%M:%S%z")

        if data["statistics"]:
            if data["statistics"]["anime"]:
                data["statistics"]["anime"] = JikanStatisticsStruct(
                    **data["statistics"]["anime"]
                )
            if data["statistics"]["manga"]:
                data["statistics"]["manga"] = JikanStatisticsStruct(
                    **data["statistics"]["manga"]
                )
            data["statistics"] = JikanStatistics(**data["statistics"])

        if data["favorites"]:
            if data["favorites"]["anime"]:
                for anime in data["favorites"]["anime"]:
                    anime["images"]["jpg"] = JikanImageStruct(**anime["images"]["jpg"])
                    anime["images"]["webp"] = JikanImageStruct(
                        **anime["images"]["webp"]
                    )
                    anime["images"] = JikanImages(**anime["images"])
                data["favorites"]["anime"] = [
                    JikanUserTitleStruct(**anime)
                    for anime in data["favorites"]["anime"]
                ]
            if data["favorites"]["manga"]:
                for manga in data["favorites"]["manga"]:
                    manga["images"]["jpg"] = JikanImageStruct(**manga["images"]["jpg"])
                    manga["images"]["webp"] = JikanImageStruct(
                        **manga["images"]["webp"]
                    )
                    manga["images"] = JikanImages(**manga["images"])
                data["favorites"]["manga"] = [
                    JikanUserTitleStruct(**manga)
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
                    JikanUserTitleStruct(**character)
                    for character in data["favorites"]["characters"]
                ]
            if data["favorites"]["people"]:
                for person in data["favorites"]["people"]:
                    person["images"]["jpg"] = JikanImageStruct(
                        **person["images"]["jpg"]
                    )
                    person["images"] = JikanImages(**person["images"])
                data["favorites"]["people"] = [
                    JikanUserTitleStruct(**person)
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
                    anime["entry"]["images"] = JikanImages(**anime["entry"]["images"])
                    anime["entry"] = JikanUserTitleStruct(**anime["entry"])
                    anime["date"] = datetime.strptime(
                        anime["date"], "%Y-%m-%dT%H:%M:%S%z"
                    )
                data["updates"]["anime"] = [
                    JikanUpdateEntry(**anime) for anime in data["updates"]["anime"]
                ]
            if data["updates"]["manga"]:
                for manga in data["updates"]["manga"]:
                    manga["entry"]["images"]["jpg"] = JikanImageStruct(
                        **manga["entry"]["images"]["jpg"]
                    )
                    manga["entry"]["images"]["webp"] = JikanImageStruct(
                        **manga["entry"]["images"]["webp"]
                    )
                    manga["entry"]["images"] = JikanImages(**manga["entry"]["images"])
                    manga["entry"] = JikanUserTitleStruct(**manga["entry"])
                    manga["date"] = datetime.strptime(
                        manga["date"], "%Y-%m-%dT%H:%M:%S%z"
                    )
                data["updates"]["manga"] = [
                    JikanUpdateEntry(**manga) for manga in data["updates"]["manga"]
                ]
            data["updates"] = JikanUserStatus(**data["updates"])

        return JikanUserStruct(**data)

    async def get_user_clubs(self, username: str) -> list[dict]:
        """Get user joined clubs

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
                    defineJikanException(resp.status, resp.reason)
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
                            defineJikanException(resp.status, resp.reason)
            return clubs
        except Exception as e:
            defineJikanException(601, e)

    async def get_user_data(self, username: str) -> JikanUserStruct:
        """Get user data

        Args:
            username (str): MyAnimeList username

        Actions:
            If Jikan took too long to respond, it will try again in multiples of 3 seconds for exponential backoff

        Returns:
            dict: User data
        """
        self.cache_expiration_time = 43200
        cache_file_path = self.get_cache_file_path(f"user/{username}.json")
        cached_file = self.read_cached_data(cache_file_path)
        if cached_file:
            return self.user_dict_to_dataclass(cached_file)

        retries = 0
        while retries < 3:
            try:
                async with self.session.get(
                    f"{self.base_url}/users/{username}/full"
                ) as resp:
                    if resp.status in [200, 304]:
                        res = await resp.json()
                        res: dict = res["data"]
                    else:
                        raise Exception(await resp.json())
                self.write_data_to_cache(res, cache_file_path)
                return self.user_dict_to_dataclass(res)
            except Exception as e:
                retries += 1
                if retries == 3:
                    errcode: int = e.status_code if hasattr(e, "status_code") else 500
                    errmsg: str | dict = e.message if hasattr(e, "message") else e
                    defineJikanException(errcode, errmsg)
                else:
                    backoff_time = 3**retries
                    await asyncio.sleep(backoff_time)

    async def get_user_by_id(self, user_id: int) -> JikanUserStruct:
        """Get user data from their MAL ID

        Args:
            user_id (int): MyAnimeList user ID

        Actions:
            If Jikan took too long to respond, it will try again in multiples of 3 seconds for exponential backoff

        Returns:
            dict: User data
        """
        async with self.session.get(
            f"{self.base_url}/users/userbyid/{user_id}"
        ) as resp:
            if resp.status in [200, 304]:
                res = await resp.json()
                res: str = res["data"]["username"]
            else:
                raise Exception(await resp.json())
        gud = await self.get_user_data(res)
        return gud

    async def get_anime_data(self, anime_id: int) -> JikanAnimeStruct:
        """Get anime data

        Args:
            anime_id (int): MyAnimeList anime ID

        Returns:
            dict: Anime data
        """
        cache_file_path = self.get_cache_file_path(f"anime/{anime_id}.json")
        cached_file = self.read_cached_data(cache_file_path)
        if cached_file:
            return self.anime_dict_to_dataclass(cached_file)
        try:
            async with self.session.get(
                f"{self.base_url}/anime/{anime_id}/full"
            ) as resp:
                if resp.status in [200, 304]:
                    res = await resp.json()
                    res = res["data"]
                else:
                    raise Exception(await resp.text())
            self.write_data_to_cache(res, cache_file_path)
            return self.anime_dict_to_dataclass(res)
        except Exception as e:
            errcode: int = e.status_code if hasattr(e, "status_code") else 500
            errmsg: str | dict = e.message if hasattr(e, "message") else e
            defineJikanException(errcode, errmsg)

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
            data (any): Data to write
            cache_file_name (str): Cache file name
        """
        cache_data = {"timestamp": time.time(), "data": data}
        os.makedirs(os.path.dirname(cache_file_path), exist_ok=True)
        with open(cache_file_path, "w") as cache_file:
            json.dump(cache_data, cache_file)
