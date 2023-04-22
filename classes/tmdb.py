import json
import os
import time
from enum import Enum

import aiohttp

from modules.const import TMDB_API_KEY


class TheMovieDb:
    def __init__(self, api_key: str = TMDB_API_KEY):
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
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        await self.session.close()

    class MediaType(Enum):
        TV = SHOW = "tv"
        MOVIE = "movie"

    async def get_nsfw_status(self, id: int, media_type: MediaType | str = MediaType.TV) -> bool:
        if isinstance(media_type, str):
            media_type = self.MediaType(media_type)
        cache_file_path = self.get_cache_path(f"{media_type.value}/{id}.json")
        cached_data = self.read_cache(cache_file_path)
        if cached_data is not None:
            return cached_data
        if media_type == self.MediaType.TV:
            url = f"{self.base_url}tv/{id}"
        elif media_type == self.MediaType.MOVIE:
            url = f"{self.base_url}movie/{id}"
        else:
            raise ValueError("Invalid mediaType")
        async with self.session.get(url, params=self.params) as resp:
            jsonText = await resp.text()
            jsonFinal = json.loads(jsonText)
        self.write_cache(cache_file_path, jsonFinal["adult"])
        return jsonFinal["adult"]

    def get_cache_path(self, cache_name: str):
        return os.path.join(self.cache_directory, cache_name)

    def read_cache(self, cache_path: str):
        if os.path.exists(cache_path):
            with open(cache_path, "r") as f:
                data = json.load(f)
                age = time.time() - data["timestamp"]
                if age < self.cache_time:
                    return data["data"]
        return None

    def write_cache(self, cache_path: str, data):
        cache_data = {
            "timestamp": time.time(),
            "data": data,
        }
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, "w") as f:
            json.dump(cache_data, f)


__all__ = ["TheMovieDb"]
