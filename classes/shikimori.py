import aiohttp
from dataclasses import dataclass
from enum import Enum
from typing import Literal
from datetime import datetime
from classes.excepts import ProviderHttpError

from modules.const import SHIKIMORI_APPLICATION_NAME as USER_AGENT, SHIKIMORI_CLIENT_ID


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
    statuses: Statuses
    full_statuses: Statuses
    scores: Stats
    types: Stats
    ratings: Stats
    activity: list[ShikimoriActivityStruct]
    has_anime: bool
    has_manga: bool
    genres: list | None
    studios: list | None
    publishers: list | None


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


class Shikimori:
    """Shikimori API wrapper"""

    def __init__(self):
        """Init Shikimori class"""
        self.base_url = "https://shikimori.one/api/"
        self.headers = {}
        self.params = {}
        self.session = None

    async def __aenter__(self):
        """Async enter"""
        self.session = aiohttp.ClientSession()
        self.headers = {
            "User-Agent": USER_AGENT
        }
        self.params = {
            "client_id": SHIKIMORI_CLIENT_ID
        }
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async exit"""
        await self.session.close()

    async def _request(self, method: str, url: str, **kwargs):
        """Make request"""
        async with self.session.request(method, url, headers=self.headers, **kwargs) as response:
            if response.status != 200:
                raise ProviderHttpError(response.reason, response.status)
            return await response.json()

    async def get_user(self, user_id: int | str, is_nickname: bool = True) -> ShikimoriUserStruct:
        """
        Get user information

        Args:
            user_id (int | str): User ID
            is_nickname (bool): Is user ID a nickname? Defaults to True

        Returns:
            ShikimoriUserStruct: User information
        """
        params = self.params.copy()
        if is_nickname:
            params['is_nickname'] = '1'
        data: dict = await self._request("GET", f"{self.base_url}users/{user_id}", params=params)
        user = ShikimoriUserStruct(
            id=data["id"],
            nickname=data["nickname"],
            avatar=data["avatar"],
            image=ShikimoriImageSizes(
                x160=data["image"]["x160"],
                x148=data["image"]["x148"],
                x80=data["image"]["x80"],
                x64=data["image"]["x64"],
                x48=data["image"]["x48"],
                x32=data["image"]["x32"],
                x16=data["image"]["x16"],
            ),
            last_online_at=datetime.strptime(data["last_online_at"], "%Y-%m-%dT%H:%M:%S.%f%z"),
            url=data["url"],
            name=data["name"],
            sex=data["sex"],
            full_years=data["full_years"],
            last_online=data["last_online"],
            website=data["website"],
            location=data["location"],
            banned=data["banned"],
            about=data["about"],
            about_html=data["about_html"],
            common_info=data["common_info"],
            show_comments=data["show_comments"],
            in_friends=data["in_friends"],
            is_ignored=data["is_ignored"],
            stats=ShikimoriStatistics(
                statuses=Statuses(
                    anime=[
                        ShikimoriStatsStruct(
                            id=a["id"],
                            grouped_id=a["grouped_id"],
                            name=a["name"],
                            size=a["size"],
                            type=a["type"]
                        ) for a in data["stats"]["statuses"]["anime"]
                    ],
                    manga=[
                        ShikimoriStatsStruct(
                            id=a["id"],
                            grouped_id=a["grouped_id"],
                            name=a["name"],
                            size=a["size"],
                            type=a["type"]
                        ) for a in data["stats"]["statuses"]["manga"]
                    ]
                ),
                full_statuses=Statuses(
                    anime=[
                        ShikimoriStatsStruct(
                            id=a["id"],
                            grouped_id=a["grouped_id"],
                            name=a["name"],
                            size=a["size"],
                            type=a["type"]
                        ) for a in data["stats"]["full_statuses"]["anime"]
                    ],
                    manga=[
                        ShikimoriStatsStruct(
                            id=a["id"],
                            grouped_id=a["grouped_id"],
                            name=a["name"],
                            size=a["size"],
                            type=a["type"]
                        ) for a in data["stats"]["full_statuses"]["manga"]
                    ]
                ),
                scores=Stats(
                    anime=[
                        ShikimoriGroupStruct(
                            name=a["name"],
                            value=a["value"],
                        ) for a in data["stats"]["scores"]["anime"]
                    ],
                    manga=[
                        ShikimoriGroupStruct(
                            name=a["name"],
                            value=a["value"],
                        ) for a in data["stats"]["scores"]["manga"]
                    ]
                ),
                types=Stats(
                    anime=[
                        ShikimoriGroupStruct(
                            name=a["name"],
                            value=a["value"],
                        ) for a in data["stats"]["types"]["anime"]
                    ],
                    manga=[
                        ShikimoriGroupStruct(
                            name=a["name"],
                            value=a["value"],
                        ) for a in data["stats"]["types"]["manga"]
                    ]
                ),
                ratings=Stats(
                    anime=[
                        ShikimoriGroupStruct(
                            name=a["name"],
                            value=a["value"],
                        ) for a in data["stats"]["ratings"]["anime"]
                    ],
                    manga=None
                ),
                studios=data["stats"]["studios"],
                genres=data["stats"]["genres"],
                publishers=data["stats"]["publishers"],
                has_anime=data["stats"]["has_anime?"],
                has_manga=data["stats"]["has_manga?"],
                activity=[
                    ShikimoriActivityStruct(
                        name=[
                            # convert epoch to datetime
                            datetime.fromtimestamp(a["name"][0]),
                            datetime.fromtimestamp(a["name"][1])
                        ],
                        value=a["value"]
                    ) for a in data["stats"]["activity"]
                ],
            ),
            style_id=data["style_id"]
        )

        return user
