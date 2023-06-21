from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Literal

import aiohttp

from classes.cache import Caching
from classes.excepts import ProviderHttpError
from modules.const import (SHIKIMORI_APPLICATION_NAME, SHIKIMORI_CLIENT_ID,
                           USER_AGENT)

Cache = Caching(cache_directory="cache/shikimori", cache_expiration_time=43200)


@dataclass
class ShikimoriImageSizes:
    """Shikimori image sizes"""

    x160: str
    """160x160"""
    x148: str
    """148x148"""
    x80: str
    """80x80"""
    x64: str
    """64x64"""
    x48: str
    """48x48"""
    x32: str
    """32x32"""
    x16: str
    """16x16"""


@dataclass
class ShikimoriStatsStruct:
    """Shikimori stats struct"""

    id: int
    """ID"""
    grouped_id: str
    """Grouped ID"""
    name: str
    """Name"""
    size: int
    """Size/Count"""
    type: Literal["Anime", "Manga"]
    """Media Type"""


@dataclass
class ShikimoriGroupStruct:
    """Shikimori group struct, for scores, media format, and age rating"""

    name: str
    """Name"""
    value: int
    """Value"""


@dataclass
class ShikimoriActivityStruct(ShikimoriGroupStruct):
    """Shikimori activity struct"""

    name: list[datetime]
    """Time, from and to"""


@dataclass
class Statuses:
    """Statuses"""

    anime: list[ShikimoriStatsStruct]
    """Anime statuses"""
    manga: list[ShikimoriStatsStruct]
    """Manga statuses"""


@dataclass
class Stats:
    """Stats"""

    anime: list[ShikimoriGroupStruct]
    """Anime stats"""
    manga: list[ShikimoriGroupStruct] | None = None
    """Manga stats, does not exist in age rating"""


@dataclass
class ShikimoriStatistics:
    """Shikimori statistics"""

    statuses: Statuses
    """Statuses, combine reconsume and current"""
    full_statuses: Statuses
    """Full statuses"""
    scores: Stats
    """Scores"""
    types: Stats
    """Types"""
    ratings: Stats
    """Ratings"""
    activity: list[ShikimoriActivityStruct]
    """Activity"""
    has_anime: bool
    """Has anime?"""
    has_manga: bool
    """Has manga?"""
    genres: list | None
    """Genres"""
    studios: list | None
    """Studios"""
    publishers: list | None
    """Publishers"""


@dataclass
class ShikimoriFavoriteStruct:
    """Shikimori favorite struct"""

    id: int
    """ID"""
    name: str
    """Name in English/Romaji"""
    russian: str
    """Name in Russian"""
    image: str
    """Image path"""
    url: str | None = None
    """URL"""


@dataclass
class ShikimoriFavorites:
    """Dataclass for user's favorites"""

    animes: list[ShikimoriFavoriteStruct] | None = None
    """Anime"""
    mangas: list[ShikimoriFavoriteStruct] | None = None
    """Manga"""
    ranobe: list[ShikimoriFavoriteStruct] | None = None
    """Light Novels"""
    characters: list[ShikimoriFavoriteStruct] | None = None
    """Characters"""
    people: list[ShikimoriFavoriteStruct] | None = None
    """People"""
    mangakas: list[ShikimoriFavoriteStruct] | None = None
    """Comic Artist"""
    seyu: list[ShikimoriFavoriteStruct] | None = None
    """Voice Actors"""
    producers: list[ShikimoriFavoriteStruct] | None = None
    """Producers"""


class ShikimoriUserGender(Enum):
    """Enum of user gender"""

    MALE = "male"
    FEMALE = "female"
    UNKNOWN = ""


@dataclass
class ShikimoriUserStruct:
    """Shikimori user struct, stores user data"""

    id: int
    """User ID"""
    nickname: str
    """User nickname"""
    avatar: str
    """User avatar, x48"""
    image: ShikimoriImageSizes
    """User avatar, contains all sizes"""
    last_online_at: datetime
    """Last online in formatted datetime, actual: %Y-%m-%dT%H:%M:%S.%f%z"""
    url: str
    """User profile URL"""
    name: str | None
    """User name"""
    sex: ShikimoriUserGender
    """Gender"""
    full_years: int | None
    """User's age"""
    last_online: str | None
    """Last online string in Russian"""
    website: str | None
    """User's website"""
    location: str | None
    """User's location"""
    banned: bool
    """Is user banned from platform?"""
    about: str | None
    """About user in BBCODE"""
    about_html: str | None
    """About user in HTML"""
    common_info: list[str] | None
    """Common info about user"""
    show_comments: bool
    """Show comments on profile?"""
    in_friends: bool | None
    """Is user friend of current logged in user?"""
    is_ignored: bool | None
    """Is user ignored by current logged in user?"""
    stats: ShikimoriStatistics
    """User stats"""
    style_id: int | None
    """User style ID"""
    favourites: ShikimoriFavorites | None = None
    """User favorites"""


class Shikimori:
    """Shikimori API wrapper"""

    def __init__(self):
        """Init Shikimori class"""
        self.base_url = "https://shikimori.me/api/"
        self.headers = {}
        self.params = {}
        self.session = None

    async def __aenter__(self):
        """Async enter"""
        self.session = aiohttp.ClientSession()
        self.headers = {
            "User-Agent": USER_AGENT.replace(
                "RyuuzakiRyuusei", SHIKIMORI_APPLICATION_NAME
            ),
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
        }
        self.params = {"client_id": SHIKIMORI_CLIENT_ID}
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async exit"""
        await self.session.close()

    async def _request(self, method: str, url: str, **kwargs):
        """Make request"""
        async with self.session.request(
            method, url, headers=self.headers, **kwargs
        ) as response:
            if response.status != 200:
                raise ProviderHttpError(response.reason, response.status)
            return await response.json()

    @staticmethod
    def _user_dict_to_dataclass(data: dict) -> ShikimoriUserStruct:
        """
        Convert user dict to dataclass

        Args:
            data (dict): User dict

        Returns:
            ShikimoriUserStruct: User dataclass
        """
        data["image"] = ShikimoriImageSizes(**data["image"])
        data["last_online_at"] = datetime.strptime(
            data["last_online_at"], "%Y-%m-%dT%H:%M:%S.%f%z"
        )
        data["stats"]["statuses"]["anime"] = [ShikimoriStatsStruct(
            **a) for a in data["stats"]["statuses"]["anime"]]
        data["stats"]["statuses"]["manga"] = [ShikimoriStatsStruct(
            **a) for a in data["stats"]["statuses"]["manga"]]
        data["stats"]["statuses"] = Statuses(**data["stats"]["statuses"])
        data["stats"]["full_statuses"]["anime"] = [ShikimoriStatsStruct(
            **a) for a in data["stats"]["full_statuses"]["anime"]]
        data["stats"]["full_statuses"]["manga"] = [ShikimoriStatsStruct(
            **a) for a in data["stats"]["full_statuses"]["manga"]]
        data["stats"]["full_statuses"] = Statuses(
            **data["stats"]["full_statuses"])
        data["stats"]["scores"]["anime"] = [
            ShikimoriGroupStruct(**a) for a in data["stats"]["scores"]["anime"]
        ]
        data["stats"]["scores"]["manga"] = [
            ShikimoriGroupStruct(**a) for a in data["stats"]["scores"]["manga"]
        ]
        data["stats"]["scores"] = Stats(**data["stats"]["scores"])
        data["stats"]["types"]["anime"] = [
            ShikimoriGroupStruct(**a) for a in data["stats"]["types"]["anime"]
        ]
        data["stats"]["types"]["manga"] = [
            ShikimoriGroupStruct(**a) for a in data["stats"]["types"]["manga"]
        ]
        data["stats"]["types"] = Stats(**data["stats"]["types"])
        data["stats"]["ratings"]["anime"] = [ShikimoriGroupStruct(
            **a) for a in data["stats"]["ratings"]["anime"]]
        data["stats"]["ratings"]["manga"] = None
        data["stats"]["ratings"] = Stats(**data["stats"]["ratings"])
        data["stats"]["activity"] = [
            ShikimoriActivityStruct(
                name=[
                    datetime.fromtimestamp(a["name"][0], tz=timezone.utc),
                    datetime.fromtimestamp(a["name"][1], tz=timezone.utc),
                ],
                value=a["value"],
            )
            for a in data["stats"]["activity"]
        ]
        data["stats"]["has_anime"] = data["stats"]["has_anime?"]
        del data["stats"]["has_anime?"]
        data["stats"]["has_manga"] = data["stats"]["has_manga?"]
        del data["stats"]["has_manga?"]
        data["stats"] = ShikimoriStatistics(**data["stats"])
        if data.get("favourites", None):
            for k, v in data["favourites"].items():
                data["favourites"][k] = (
                    [ShikimoriFavoriteStruct(**a)
                     for a in data["favourites"][k]]
                    if v is not None or len(v) > 0
                    else None
                )
            data["favourites"] = ShikimoriFavorites(**data["favourites"])
        data["sex"] = ShikimoriUserGender(data["sex"])
        user = ShikimoriUserStruct(**data)
        return user

    async def get_user(
        self, user_id: int | str, is_nickname: bool = True
    ) -> ShikimoriUserStruct:
        """
        Get user information

        Args:
            user_id (int | str): User ID
            is_nickname (bool): Is user ID a nickname? Defaults to True

        Returns:
            ShikimoriUserStruct: User information
        """
        cache_file_path = Cache.get_cache_file_path(f"user/{user_id}.json")
        cached_data = Cache.read_cached_data(cache_file_path)
        if cached_data is not None:
            formatted_data = self._user_dict_to_dataclass(cached_data)
            return formatted_data
        params = self.params.copy()
        if is_nickname:
            params["is_nickname"] = "1"
        data: dict = await self._request(
            "GET", f"{self.base_url}users/{user_id}", params=params
        )
        user_id_int = data["id"]
        favs = f"{self.base_url}users/{user_id_int}/favourites"
        favourites: dict = await self._request(
            "GET",
            favs,
        )
        data["favourites"] = favourites
        Cache.write_data_to_cache(data=data, cache_path=cache_file_path)
        user = self._user_dict_to_dataclass(data)
        return user
