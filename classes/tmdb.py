import json
from enum import Enum
from typing import Literal

import aiohttp

from classes.cache import Caching
from classes.excepts import ProviderTypeError
from modules.const import TMDB_API_KEY, USER_AGENT

Cache = Caching(cache_directory="cache/tmdb", cache_expiration_time=2592000)


class TheMovieDb:
    """The Movie DB Wrapper"""

    def __init__(self, api_key: str = TMDB_API_KEY):
        """
        Initialize the TheMovieDb API Wrapper

        Args:
            api_key (str): TheMovieDb API key, defaults to TMDB_API_KEY
        """
        self.api_key = api_key
        self.session = None
        self.base_url = "https://api.themoviedb.org/3/"
        self.params = {
            "api_key": self.api_key,
            "language": "en-US",
        }

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
        """
        Get the NSFW status of a TV show or movie

        Args:
            media_id (int): The ID of the TV show or movie
            media_type (MediaType | Literal["movie","tv"]): The media type, defaults to MediaType.TV

        Returns:
            bool: True if the TV show or movie is NSFW, False otherwise
        """
        if isinstance(media_type, self.MediaType):
            media_type = media_type.value
        cache_file_path = Cache.get_cache_path(
            f"{media_type.value}/{media_id}.json")
        cached_data = Cache.read_cache(cache_file_path)
        if cached_data is not None:
            return cached_data
        if media_type in ["tv", "movie"]:
            url = f"{self.base_url}{media_type}/{media_id}"
        else:
            raise ProviderTypeError("Invalid mediaType", [
                                    "tv", "movie", self.MediaType])
        async with self.session.get(url, params=self.params) as resp:
            if resp.status != 200:
                return False
            jsonText = await resp.text()
            jsonFinal = json.loads(jsonText)
            Cache.write_cache(cache_file_path, jsonFinal["adult"])
            return jsonFinal["adult"]


__all__ = ["TheMovieDb"]
