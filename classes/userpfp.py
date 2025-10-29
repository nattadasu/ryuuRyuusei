import json

import aiohttp
from fake_useragent import FakeUserAgent  # type: ignore
from interactions import Snowflake

from classes.cache import Caching

USER_AGENT = FakeUserAgent(browsers=["chrome", "edge", "opera"]).random
Cache = Caching(cache_directory="cache/userpfp", cache_expiration_time=216000)


class UserPFP:
    """UserPFP wrapper"""

    def __init__(self):
        """Initialize the UserBackground class."""
        self.raw_url = (
            "https://raw.githubusercontent.com/UserPFP/UserPFP/main/source/data.json"
        )
        self.session = None
        self.headers = None

    async def __aenter__(self):
        """Enter the async context manager."""
        self.headers = {"User-Agent": USER_AGENT}
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Exit the async context manager."""
        await self.close()

    async def close(self):
        """Close the aiohttp session."""
        await self.session.close()

    async def _fetch_background(self) -> dict:
        """
        Fetch the background from the GitHub repository.

        Returns:
            dict: The background data.
        """
        print("Fetching UserPFP from GitHub...")
        async with self.session.get(self.raw_url) as response:
            resp = await response.text()
            data = json.loads(resp)
            return data

    @staticmethod
    async def _find_user(user_id: Snowflake, data: dict[str, str]) -> str | None:
        """
        Find user on the dict, then return datastruct

        Args:
            user_id (Snowflake): User's Discord ID
            data: UserPFP's dict

        Return:
            str: The user profile picture.
            None: If user can't be found
        """
        # Find user
        return data.get(str(user_id), None)

    async def get_picture(self, user_id: Snowflake) -> str | None:
        """
        Get the user profile picture from the GitHub repository.

        Args:
            user_id (Snowflake): User's Discord ID

        Returns:
            str: The user profile picture.
            None: If user can't be found
        """
        data: dict[str, dict[str, str]] | None
        # Get cache path
        cache_path = Cache.get_cache_path("userpfp.json")
        # Read cache
        data = Cache.read_cache(cache_path)
        # If cache is expired, fetch from GitHub
        if data is None:
            data = await self._fetch_background()
            Cache.write_cache(cache_path, data)
        # Find user
        user = await self._find_user(user_id, data["avatars"])
        return user
