from dataclasses import dataclass
from typing import Any

import aiohttp
from interactions import Snowflake

from classes.cache import Caching
from modules.const import USER_AGENT

# 2 days and half
day2h = 60 * 60 * 60
Cache = Caching(cache_directory="cache/usrbg", cache_expiration_time=day2h)

BASE_URL = "https://usrbg.is-hardly.online"


@dataclass
class UsrBgDataStruct:
    """A dataclass pointing to the user's background"""

    users: dict[str, str]
    endpoint: str = BASE_URL
    bucket: str = "usrbg"
    prefix: str = "v2/"

    def get_user_banner(self, user_id: Snowflake) -> str:
        """Get the user's background from the cache or the API"""

        if str(user_id) in self.users:
            loc = self.users[str(user_id)]
            return f"{self.endpoint}/{self.bucket}/{self.prefix}{str(user_id)}?{loc}"

        raise ValueError(
            "User not found in the UsrBG Database. Either is cache is old, or the user has no background."
        )


class UsrBg:
    """A class to interact with the UsrBG API"""

    def __init__(self):
        """Initialize the class"""
        self.headers = {"User-Agent": USER_AGENT}
        self.session = None
        self.database: dict[str, str] = {}

    async def __aenter__(self):
        """Return the class instance"""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):  # type: ignore
        """Close the session"""
        await self.session.close() if self.session else None

    async def _fetch_background(self) -> Any:
        """Get the user's background from the API"""
        cache_path = Cache.get_cache_path("usrbg.json")
        self.database = Cache.read_cache(cache_path)
        if self.database:
            return self.database

        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(f"{BASE_URL}/users") as resp:
                if resp.status == 200:
                    self.database = await resp.json()
                    Cache.write_cache(cache_path, self.database)
                    return self.database
                resp.raise_for_status()

    async def get_background(self, user_id: Snowflake) -> str:
        """Get the user's background from the API"""
        if not self.database:
            await self._fetch_background()

        resp = UsrBgDataStruct(**self.database).get_user_banner(user_id)
        return resp
