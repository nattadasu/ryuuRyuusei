import json
import os
import time
from enum import Enum

import aiohttp

from classes.excepts import ProviderHttpError


class Kitsu:
    """Kitsu API wrapper"""

    def __init__(self):
        """Initialize the Kitsu API Wrapper"""
        self.session = aiohttp.ClientSession()
        self.base_url = "https://kitsu.io/api/edge/"
        self.params = {
            # public client ID provided by Kitsu themselves
            'client_id': 'dd031b32d2f56c990b1425efe6c42ad847e7fe3ab46bf1299f05ecd856bdb7dd'
        }
        self.content_type = "application/vnd.api+json"
        self.cache_directory = "cache/kitsu"
        self.cache_time = 86400

    def __aenter__(self):
        """Enter the async context manager"""
        return self

    def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context manager"""
        self.close()

    def close(self):
        """Close the aiohttp session"""
        self.session.close()

    class MediaType(Enum):
        """Media type enum"""
        ANIME = "anime"
        MANGA = "manga"

    async def get_anime(self, anime_id: int, media_type: MediaType | str = MediaType.ANIME) -> dict:
        """Get anime data

        Args:
            anime_id (int): The anime ID
            media_type (MediaType | str, optional): The media type. Defaults to MediaType.ANIME.

        Returns:
            dict: Anime data
        """
        if isinstance(media_type, str):
            media_type = self.MediaType(media_type)
        cache_file_path = self.get_cache_path(
            f"{media_type.value}/{anime_id}.json")
        cached_data = self.read_cache(cache_file_path)
        if cached_data is not None:
            return cached_data
        url = f"{self.base_url}{media_type.value}/{anime_id}"
        async with self.session.get(url, params=self.params) as resp:
            if resp.status != 200:
                raise ProviderHttpError(resp.text(), resp.status)
            jsonText = await resp.text()
            jsonFinal = json.loads(jsonText)
        self.write_cache(cache_file_path, jsonFinal)
        return jsonFinal

    async def resolve_slug(self, slug: str, media_type: MediaType | str = MediaType.ANIME) -> dict:
        """Resolve slug to anime ID

        Args:
            slug (str): The anime slug
            media_type (MediaType | str, optional): The media type. Defaults to MediaType.ANIME.

        Returns:
            dict: Anime data
        """
        if isinstance(media_type, str):
            media_type = self.MediaType(media_type)
        cache_file_path = self.get_cache_path(
            f"{media_type.value}/slug/{slug}.json")
        cached_data = self.read_cache(cache_file_path)
        if cached_data is not None:
            return cached_data
        url = f"{self.base_url}{media_type.value}/?filter[slug]={slug}"
        async with self.session.get(url, params=self.params) as resp:
            if resp.status != 200:
                raise ProviderHttpError(resp.text(), resp.status)
            jsonText = await resp.text()
            jsonFinal = json.loads(jsonText)
        self.write_cache(cache_file_path, jsonFinal)
        return jsonFinal

    def get_cache_path(self, file_name: str) -> str:
        """Get the cache path"""
        return os.path.join(self.cache_directory, file_name)

    def read_cache(self, cache_path: str):
        """Read the cache"""
        if os.path.exists(cache_path):
            with open(cache_path, "r") as f:
                data = json.load(f)
                age = time.time() - data["timestamp"]
                if age < self.cache_time:
                    return data["data"]
        return None

    def write_cache(self, cache_path: str, data):
        """Write the cache"""
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, "w") as f:
            json.dump({"timestamp": time.time(), "data": data}, f)
