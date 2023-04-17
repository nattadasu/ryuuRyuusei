import json
import os
import time

from aiohttp import ClientSession

from classes.excepts import ProviderHttpError, ProviderTypeError
from modules.const import RAWG_API_KEY


class RawgAPI:
    def __init__(self, key: str = RAWG_API_KEY):
        if key is None:
            raise ProviderHttpError("No API key provided", 401)
        self.base_url = "https://api.rawg.io/api"
        self.params = {"key": key}
        self.session = None
        self.cache_directory = 'cache/rawg'
        self.cache_expiration_time = 86400  # 1 day in seconds

    async def __aenter__(self):
        self.session = ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def search(self, query: str) -> dict:
        """Search game on RAWG"""
        self.params["search"] = query
        self.params["page_size"] = 5
        async with self.session.get(self.base_url + "/games", params=self.params) as resp:
            if resp.status == 200:
                rawgRes = await resp.json()
                return rawgRes["results"]
            else:
                raise ProviderHttpError(
                    f"RAWG API returned {resp.status}. Reason: {resp.text()}", resp.status)

    async def get_data(self, slug: str) -> dict:
        """Get information of a title in RAWG"""
        cache_file_path = self.get_cache_file_path(f'{slug}.json')
        cached_data = self.read_cached_data(cache_file_path)
        if cached_data is not None:
            return cached_data
        async with self.session.get(f"https://api.rawg.io/api/games/{slug}", params=self.params) as resp:
            if resp.status == 200:
                rawgRes = await resp.json()
            else:
                raise ProviderHttpError(
                    f"RAWG API returned {resp.status}. Reason: {resp.text()}", resp.status)
        if len(rawgRes) == 0:
            raise ProviderTypeError("**No results found!**", dict)
        self.write_data_to_cache(cache_file_path, rawgRes)
        return rawgRes

    def get_cache_file_path(self, cache_file_name: str) -> str:
        """Get cache file path

        Args:
            cache_file_name (str): Cache file name

        Returns:
            str: Cache file path
        """
        return os.path.join(self.cache_directory, cache_file_name)

    def read_cached_data(self, cache_file_path: str) -> dict | None:
        """Read cached data

        Args:
            cache_file_name (str): Cache file name

        Returns:
            dict: Cached data
            None: If cache file does not exist
        """
        if os.path.exists(cache_file_path):
            with open(cache_file_path, 'r') as cache_file:
                cache_data = json.load(cache_file)
                cache_age = time.time() - cache_data['timestamp']
                if cache_age < self.cache_expiration_time:
                    return cache_data['data']
        return None

    def write_data_to_cache(self, cache_file_path, data):
        """Write data to cache"""
        cache_data = {'timestamp': time.time(), 'data': data}
        os.makedirs(os.path.dirname(cache_file_path), exist_ok=True)
        with open(cache_file_path, 'w') as cache_file:
            json.dump(cache_data, cache_file)

    async def close(self):
        await self.session.close()
