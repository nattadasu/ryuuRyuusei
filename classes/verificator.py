"""
Verificator class

This class is used to verify user input during registration
"""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from uuid import uuid4

from classes.cache import Caching

Cache = Caching(cache_directory="cache/verify", cache_expiration_time=43200)


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
        cache_file_path = Cache.get_cache_file_path(f"{discord_id}.json")
        data = VerificatorUser(
            uuid=identifier,
            discord_id=discord_id,
            mal_username=mal_username,
            epoch_time=int(datetime.now(timezone.utc).timestamp()),
        )
        Cache.write_data_to_cache(data.to_dict(), cache_file_path)
        return data

    @staticmethod
    def get_user_uuid(
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
        cache_file_path = Cache.get_cache_file_path(f"{discord_id}.json")
        cached_data = Cache.read_cached_data(cache_file_path)
        if cached_data is not None:
            verify = VerificatorUser(**cached_data)
            return verify
        return None
