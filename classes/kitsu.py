import json
from enum import Enum

import aiohttp

from classes.cache import Caching
from classes.excepts import ProviderHttpError
from modules.const import USER_AGENT

Cache = Caching(cache_directory="cache/kitsu", cache_expiration_time=86400)


class Kitsu:
    """Kitsu API wrapper"""

    def __init__(self):
        """Initialize the Kitsu API Wrapper"""
        self.session = None
        self.base_url = "https://kitsu.io/api/edge/"
        self.params = None

    async def __aenter__(self):
        """Enter the async context manager"""
        self.session = aiohttp.ClientSession(
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "application/vnd.api+json",
                "Content-Type": "application/vnd.api+json",
            }
        )
        self.params = {
            # public client ID provided by Kitsu themselves
            "client_id": "dd031b32d2f56c990b1425efe6c42ad847e7fe3ab46bf1299f05ecd856bdb7dd"
        }
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context manager"""
        await self.close()

    async def close(self):
        """Close the aiohttp session"""
        await self.session.close()

    class MediaType(Enum):
        """Media type enum"""

        ANIME = "anime"
        MANGA = "manga"

    async def get_anime(
        self, anime_id: int, media_type: MediaType | str = MediaType.ANIME
    ) -> dict:
        """
        Get anime data

        Args:
            anime_id (int): The anime ID
            media_type (MediaType | str, optional): The media type. Defaults to MediaType.ANIME.

        Returns:
            dict: Anime data
        """
        if isinstance(media_type, str):
            media_type = self.MediaType(media_type)
        cache_file_path = Cache.get_cache_path(
            f"{media_type.value}/{anime_id}.json")
        cached_data = Cache.read_cache(cache_file_path)
        if cached_data is not None:
            return cached_data
        url = f"{self.base_url}{media_type.value}/{anime_id}"
        async with self.session.get(url, params=self.params) as resp:
            if resp.status != 200:
                raise ProviderHttpError(resp.text(), resp.status)
            jsonText = await resp.text()
            jsonFinal = json.loads(jsonText)
        Cache.write_cache(cache_file_path, jsonFinal)
        return jsonFinal

    async def resolve_slug(
        self, slug: str, media_type: MediaType | str = MediaType.ANIME
    ) -> dict:
        """
        Resolve slug to anime ID

        Args:
            slug (str): The anime slug
            media_type (MediaType | str, optional): The media type. Defaults to MediaType.ANIME.

        Returns:
            dict: Anime data
        """
        if isinstance(media_type, str):
            media_type = self.MediaType(media_type)
        cache_file_path = Cache.get_cache_path(
            f"{media_type.value}/slug/{slug}.json")
        cached_data = Cache.read_cache(cache_file_path)
        if cached_data is not None:
            return cached_data
        url = f"{self.base_url}{media_type.value}/?filter[slug]={slug}"
        async with self.session.get(url, params=self.params) as resp:
            if resp.status != 200:
                raise ProviderHttpError(resp.text(), resp.status)
            jsonText = await resp.text()
            jsonFinal = json.loads(jsonText)
        Cache.write_cache(cache_file_path, jsonFinal)
        return jsonFinal
