import json
import os
import time
from enum import Enum

import aiohttp

from classes.excepts import ProviderHttpError, ProviderTypeError
from modules.const import traktHeader


class Trakt:
    def __init__(self):
        self.session = None
        self.base_url = "https://api.trakt.tv/"
        self.cache_directory = "cache/trakt"
        self.cache_time = 86400
        self.headers = traktHeader

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        await self.session.close()

    class Platform(Enum):
        IMDB = "imdb"
        TMDB = "tmdb"

    class MediaType(Enum):
        TV = SHOW = ONA = "show"
        MOVIE = "movie"

    async def lookup(self, platform: Platform, id: int | str, media_type: MediaType | str) -> dict:
        if isinstance(platform, str):
            platform = self.Platform(platform)
        if isinstance(media_type, str):
            media_type = self.MediaType(media_type)
        if platform == self.Platform.TMDB and not media_type:
            raise ProviderTypeError("TMDB requires a media type", "MediaType")
        self.cache_time = 2592000
        cache_file_path = self.get_cache_path(
            f"lookup/{platform.value}/{media_type.value}/{id}.json")
        cached_data = self.read_cache(cache_file_path)
        if cached_data is not None:
            return cached_data
        if platform == self.Platform.TMDB:
            params = {"type": media_type.value}
        else:
            params = {}
        url = f"{self.base_url}search/{platform.value}/{id}"
        async with self.session.get(url, params=params) as resp:
            if resp.status != 200:
                raise ProviderHttpError(resp.text(), resp.status)
            jsonText = await resp.text()
            jsonFinal = json.loads(jsonText)
        self.write_cache(cache_file_path, jsonFinal[0])
        return jsonFinal[0]

    async def get_title_data(self, id: int | str, media_type: MediaType | str) -> dict:
        if isinstance(media_type, str):
            media_type = self.MediaType(media_type)
        cache_file_path = self.get_cache_path(f"{media_type.value}/{id}.json")
        cached_data = self.read_cache(cache_file_path)
        if cached_data is not None:
            return cached_data
        url = f"{self.base_url}{media_type.value}/{id}"
        param = {
            "extended": "full"
        }
        async with self.session.get(url, params=param) as resp:
            if resp.status != 200:
                raise ProviderHttpError(resp.text(), resp.status)
            jsonText = await resp.text()
            jsonFinal = json.loads(jsonText)
        self.write_cache(cache_file_path, jsonFinal)
        return jsonFinal

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
        with open(cache_path, "w") as f:
            json.dump({"timestamp": time.time(), "data": data}, f)
