import json
import os
import time
from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class CacheModel:
    """Cache Model"""

    timestamp: int | float
    """The timestamp of the cache file"""
    data: Any
    """The data in the cache file"""


class Caching:
    """Interface to cache data received from 3rd party APIs"""

    def __init__(
            self,
            cache_directory: str,
            cache_expiration_time: int | float):
        """
        Args:
            cache_directory (str): The directory to store cache files
            cache_expiration_time (int | float): The time in seconds before a cache file is considered expired
        """
        self.cache_directory = cache_directory
        if not os.path.exists(cache_directory):
            os.makedirs(cache_directory)
        if isinstance(cache_expiration_time, int):
            cache_expiration_time = float(cache_expiration_time)
        self.cache_expiration_time = cache_expiration_time

    def get_cache_path(self, cache_name: str) -> str:
        """
        Get the cache path of a cache file

        Args:
            cache_name (str): The cache file name

        Returns:
            str: The cache file path
        """
        return os.path.join(self.cache_directory, cache_name)

    def read_cache(
            self,
            cache_path: str,
            override_expiration_time: int | float | None = None) -> Any:
        """
        Read a cache file

        Args:
            cache_path (str): The cache file path

        Returns:
            any: The data in the cache file
            None: The cache file does not exist or is expired
        """
        if override_expiration_time is None:
            expirate_time = self.cache_expiration_time
        else:
            expirate_time = override_expiration_time
        if os.path.exists(cache_path):
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                model = CacheModel(**data)
                age = time.time() - model.timestamp
                if age < expirate_time:
                    return model.data
        return None

    @staticmethod
    def write_cache(cache_path: str, data: Any) -> None:
        """
        Write data to a cache file

        Args:
            cache_path (str): The cache file path
            data (any): The data to write

        Raises:
            Exception: Failed to write data to cache file

        Returns:
            None: None
        """
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        model = CacheModel(time.time(), data)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(asdict(model), f)

    @staticmethod
    def drop_cache(cache_path: str) -> None:
        """
        Delete a cache file

        Args:
            cache_path (str): The cache file path

        Returns:
            None: None
        """
        if os.path.exists(cache_path):
            os.remove(cache_path)

    # Aliases
    get_cache_file_path = get_cache_path
    """Legacy alias of get_cache_path"""
    read_cached_data = read_cache
    """Legacy alias of read_cache"""

    def write_data_to_cache(self, data: Any, cache_path: str) -> None:
        """
        legacy alias for write_cache by swapping the arguments order

        Args:
            data (any): The data to write
            cache_path (str): The cache file path

        Raises:
            Exception: Failed to write data to cache file

        Returns:
            None: None
        """
        self.write_cache(cache_path, data)


__all__ = ["Caching"]
