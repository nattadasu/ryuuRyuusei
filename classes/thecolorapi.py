import json
import os
import time

import aiohttp

from classes.excepts import ProviderHttpError


class TheColorApi:
    """The Color API wrapper

    This module is a wrapper for The Color API, which is used to get color information from hex, rgb, hsl, hsv, and cmyk values."""
    def __init__(self):
        """Initialize the class"""
        self.base_url = "https://www.thecolorapi.com"
        self.session = None
        self.cache_directory = 'cache/thecolorapi'
        self.cache_expiration_time = 604800  # 1 week in seconds

    async def __aenter__(self):
        """Create a session if class invoked with `with` statement"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Close the session if class invoked with `with` statement"""
        await self.session.close()

    async def close(self) -> None:
        """Close the session"""
        await self.session.close()

    async def color(self, **color):
        """Get color information from hex, rgb, hsl, hsv, or cmyk values"""
        cache_file_path = self.get_cache_file_path(color)
        cached_data = self.read_cached_data(cache_file_path)
        if cached_data is not None:
            return cached_data

        async with self.session.get(f"{self.base_url}/id", params=color) as response:
            if response.status == 200:
                data = await response.json()
                self.write_data_to_cache(cache_file_path, data)
                return data
            else:
                error_message = await response.text()
                raise ProviderHttpError(error_message, response.status)

    def get_cache_file_path(self, color_params):
        """Get the cache file from path"""
        filename = '-'.join([f"{k}_{v}" for k,
                            v in color_params.items()]) + '.json'
        return os.path.join(self.cache_directory, filename)

    def read_cached_data(self, cache_file_path):
        """Read cached data from file"""
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
