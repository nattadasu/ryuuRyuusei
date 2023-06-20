"""
Verificator class

This class is used to verify user input during registration
"""

import json
import os
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from uuid import uuid4


@dataclass
class VerificatorUser:
    """VerificatorUser dataclass"""

    uuid: str
    """UUID"""
    discord_id: int
    """Discord ID"""
    mal_username: str
    """MyAnimeList username"""
    epoch_time: int
    """Epoch time"""

    def to_dict(self):
        """Converts the VerificatorUser object to a dictionary, if needed"""
        return asdict(self)


class Verificator:
    """Verificator class"""

    def __init__(self):
        """Initialize the class"""
        self.cache_directory = "cache/verify"
        self.expire_time = 43200

    def __enter__(self):
        """Enter the class"""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the class"""

    def __del__(self):
        """Delete the class"""

    async def __aenter__(self):
        """Enter the class"""
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Exit the class"""

    @staticmethod
    def _generate_identifier() -> str:
        """
        Generate a new identifier

        Returns:
            str: Identifier
        """
        return str(uuid4())

    def save_user_uuid(
        self,
        discord_id: int,
        mal_username: str,
    ) -> VerificatorUser:
        """
        Save user UUID

        Args:
            discord_id (int): Discord ID
            mal_username (str): MyAnimeList username

        Returns:
            VerificatorUser: VerificatorUser object
        """
        identifier = self._generate_identifier()
        cache_file_path = self.get_cache_file_path(f"{discord_id}.json")
        data = VerificatorUser(
            uuid=identifier,
            discord_id=discord_id,
            mal_username=mal_username,
            epoch_time=int(datetime.now(timezone.utc).timestamp()),
        )
        self.write_data_to_cache(data.to_dict(), cache_file_path)
        return data

    def get_user_uuid(
        self,
        discord_id: int,
    ) -> VerificatorUser | None:
        """
        Get user UUID

        Args:
            discord_id (int): Discord ID

        Returns:
            VerificatorUser: VerificatorUser object
            None: If identifier does not exist
        """
        cache_file_path = self.get_cache_file_path(f"{discord_id}.json")
        cached_data = self.read_cached_data(cache_file_path)
        if cached_data is not None:
            verify = VerificatorUser(**cached_data)
            return verify
        return None

    def get_cache_file_path(self, cache_file_name: str) -> str:
        """
        Get cache file path

        Args:
            cache_file_name (str): Cache file name

        Returns:
            str: Cache file path
        """
        return os.path.join(self.cache_directory, cache_file_name)

    def read_cached_data(self, cache_file_path: str) -> dict | None:
        """
        Read cached data

        Args:
            cache_file_name (str): Cache file name

        Returns:
            dict: Cached data
            None: If cache file does not exist
        """
        if os.path.exists(cache_file_path):
            with open(cache_file_path, "r") as cache_file:
                cache_data = json.load(cache_file)
                cache_age = time.time() - cache_data["timestamp"]
                if cache_age < self.expire_time:
                    return cache_data["data"]
        return None

    @staticmethod
    def write_data_to_cache(data, cache_file_path: str):
        """
        Write data to cache

        Args:
            data (any): Data to write to cache
            cache_file_name (str): Cache file name
        """
        cache_data = {"timestamp": time.time(), "data": data}
        os.makedirs(os.path.dirname(cache_file_path), exist_ok=True)
        with open(cache_file_path, "w") as cache_file:
            json.dump(cache_data, cache_file)
