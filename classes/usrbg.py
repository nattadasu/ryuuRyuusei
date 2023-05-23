from dataclasses import dataclass

import aiohttp
import json
from interactions import Snowflake
import os
import time
from fake_useragent import FakeUserAgent

USER_AGENT = FakeUserAgent(browsers=["chrome", "edge", "opera"]).random


@dataclass
class UserBackgroundStruct:
    """A dataclass to represent user background."""

    _id: str
    """Entry ID"""
    uid: Snowflake
    """User ID"""
    img: str
    """Image URL"""
    orientation: str
    """Image orientation"""


class UserBackground:
    """usrbg wrapper"""

    def __init__(self):
        """Initialize the UserBackground class."""
        self.raw_url = "https://raw.githubusercontent.com/Discord-Custom-Covers/usrbg/master/dist/usrbg.json"
        self.cache_directory = "cache/usrbg"
        # cache for 2.5 days in seconds
        self.cache_expiration_time = 216000
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
        print("Fetching usrbg from GitHub...")
        async with self.session.get(self.raw_url) as response:
            resp = await response.text()
            data = json.loads(resp)
            return data

    async def _find_user(
        self, user_id: Snowflake, data: dict
    ) -> UserBackgroundStruct | None:
        """
        Find user on the dict, then return datastruct

        Args:
            user_id (Snowflake): User's Discord ID
            data: usrbg's dict

        Return:
            UserBackgroundStruct: Datastruct
            None: If user can't be found
        """
        # Find user
        user = next((item for item in data if item["uid"] == str(user_id)), None)
        if user is None:
            return None
        # Create datastruct
        return UserBackgroundStruct(
            _id=user["_id"],
            uid=user["uid"],
            img=user["img"],
            orientation=user["orientation"],
        )

    async def get_background(self, user_id: Snowflake) -> UserBackgroundStruct | None:
        """
        Get the user background.

        Args:
            user_id (Snowflake): User's Discord ID

        Returns:
            UserBackgroundStruct: The user background.
            None: If user can't be found
        """
        # Get cache path
        cache_path = self.get_cache_path("usrbg.json")
        # Read cache
        data = self.read_cache(cache_path)
        # If cache is expired, fetch from GitHub
        if data is None:
            data = await self._fetch_background()
            self.write_cache(cache_path, data)
        # Find user
        user = await self._find_user(user_id, data)
        return user

    def get_cache_path(self, cache_name: str):
        """
        Get the cache path of a cache file

        Args:
            cache_name (str): The cache file name
        """
        return os.path.join(self.cache_directory, cache_name)

    def read_cache(self, cache_path: str):
        """
        Read a cache file

        Args:
            cache_path (str): The cache file path

        Returns:
            any: The data in the cache file
        """
        if os.path.exists(cache_path):
            with open(cache_path, "r") as f:
                data = json.load(f)
                age = time.time() - data["timestamp"]
                if age < self.cache_expiration_time:
                    return data["data"]
        return None

    @staticmethod
    def write_cache(cache_path: str, data):
        """
        Write data to a cache file

        Args:
            cache_path (str): The cache file path
            data (any): The data to write
        """
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, "w") as f:
            json.dump({"timestamp": time.time(), "data": data}, f)
