import json
import os
import time
from enum import Enum
from typing import Literal

import aiohttp

from modules.const import TMDB_API_KEY, USER_AGENT


class TheMovieDb:
    def __init__(self, api_key: str = TMDB_API_KEY):
        """Initialize the TheMovieDb API Wrapper

        Args:
            api_key (str): TheMovieDb API key, defaults to TMDB_API_KEY"""
        self.api_key = api_key
        self.session = None
        self.base_url = "https://api.themoviedb.org/3/"
        self.params = {
            "api_key": self.api_key,
            "language": "en-US",
        }
        self.cache_directory = "cache/tmdb"
        self.cache_time = 2592000

    async def __aenter__(self):
        """Enter the async context manager"""
        self.session = aiohttp.ClientSession(
            headers={"User-Agent": USER_AGENT})
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context manager"""
        await self.close()

    async def close(self):
        """Close the aiohttp session"""
        await self.session.close()

    class MediaType(Enum):
        """Media type enum"""

        TV = SHOW = "tv"
        MOVIE = "movie"

    async def get_nsfw_status(
        self,
        media_id: int,
        media_type: MediaType | Literal["movie", "tv"] = MediaType.TV,
    ) -> bool:
        """Get the NSFW status of a TV show or movie

        Args:
            media_id (int): The ID of the TV show or movie
            media_type (MediaType | Literal["movie","tv"]): The media type, defaults to MediaType.TV

        Returns:
            bool: True if the TV show or movie is NSFW, False otherwise"""
        if isinstance(media_type, str):
            media_type = self.MediaType(media_type)
        cache_file_path = self.get_cache_path(
            f"{media_type.value}/{media_id}.json")
        cached_data = self.read_cache(cache_file_path)
        if cached_data is not None:
            return cached_data
        if media_type == self.MediaType.TV:
            url = f"{self.base_url}tv/{media_id}"
        elif media_type == self.MediaType.MOVIE:
            url = f"{self.base_url}movie/{media_id}"
        else:
            raise ValueError("Invalid mediaType")
        async with self.session.get(url, params=self.params) as resp:
            if resp.status != 200:
                return False
            jsonText = await resp.text()
            jsonFinal = json.loads(jsonText)
            self.write_cache(cache_file_path, jsonFinal["adult"])
            return jsonFinal["adult"]

    def get_cache_path(self, cache_name: str):
        """Get the cache path

        Args:
            cache_name (str): The cache name"""
        return os.path.join(self.cache_directory, cache_name)

    def read_cache(self, cache_path: str) -> dict | bool | None:
        """Read the cache

        Args:
            cache_path (str): The cache path

        Returns:
            dict | bool | None: The cache data or None if the cache is invalid"""
        if os.path.exists(cache_path):
            with open(cache_path, "r") as f:
                data = json.load(f)
                age = time.time() - data["timestamp"]
                if age < self.cache_time:
                    return data["data"]
        return None

    @staticmethod
    def write_cache(cache_path: str, data):
        """Write the cache

        Args:
            cache_path (str): The cache path
            data: The data to write"""
        cache_data = {
            "timestamp": time.time(),
            "data": data,
        }
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, "w") as f:
            json.dump(cache_data, f)


__all__ = ["TheMovieDb"]
