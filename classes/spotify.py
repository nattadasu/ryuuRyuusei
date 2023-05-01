"""Spotify API Wrapper class"""

import base64 as b64
import json
import os
import time
from enum import Enum
from typing import List, Union

import aiohttp

from classes.excepts import ProviderHttpError, ProviderTypeError
from modules.const import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, USER_AGENT


class SpotifyApi:
    """Spotify Unofficial Class"""

    def __init__(
        self,
        client_id: str = SPOTIFY_CLIENT_ID,
        client_secret: str = SPOTIFY_CLIENT_SECRET,
    ):
        """Spotify Unofficial Class

        Args:
            client_id (str, optional): Spotify Client ID. Defaults to SPOTIFY_CLIENT_ID.
            client_secret (str, optional): Spotify Client Secret. Defaults to SPOTIFY_CLIENT_SECRET.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://api.spotify.com"
        self.cache_directory = "cache/spotify"
        # cache up to 2 weeks in seconds
        self.cache_expiration_time = 1209600
        self.token = None
        self.session = None

    async def __aenter__(self):
        """Enter the session"""
        self.session = aiohttp.ClientSession(headers={"User-Agent": USER_AGENT})
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the session"""
        await self.close()

    async def close(self):
        """Close the session"""
        await self.session.close()

    async def authorize_client(self):
        """Authorize client without requiring user resource access"""
        self.cache_expiration_time = 3600
        auth = self.get_cache_file_path("auth.json")
        cached = self.read_cached_data(auth)
        if cached is not None:
            self.token = cached["access_token"]
        basic = b64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode("ascii")
        ).decode("ascii")
        async with self.session.post(
            "https://accounts.spotify.com/api/token",
            headers={"Authorization": f"Basic {basic}"},
            data={"grant_type": "client_credentials"},
        ) as response:
            if response.status == 200:
                data = await response.json()
                self.token = data["access_token"]
                self.write_data_to_cache(data, auth)
            else:
                raise ProviderHttpError(response.status, response.reason)

    class MediaType(Enum):
        """Media Type"""

        ALBUM = "album"
        ARTIST = "artist"
        PLAYLIST = "playlist"
        TRACK = "track"

    async def search(
        self,
        query: str,
        media_type: Union[List[MediaType], MediaType, str] = MediaType.TRACK,
        limit: int = 10,
        offset: int = 0,
    ) -> dict:
        """Search for a track

        Args:
            query (str): Search query
            media_type (Union[Union[List[MediaType], str], MediaType, str], optional): Media type. Defaults to MediaType.TRACK.
            limit (int, optional): Limit. Defaults to 10, max 50.
            offset (int, optional): Offset. Defaults to 0.

        Returns:
            dict: Track data
        """
        await self.authorize_client()
        if isinstance(media_type, list) and len(media_type) > 1:
            media_type = ",".join([m.value for m in media_type])
        if isinstance(media_type, self.MediaType):
            media_type = media_type.value
        if limit > 50:
            raise ProviderTypeError(
                "Limit cannot be greater than 50", "limit >= 0, <= 50"
            )
        async with self.session.get(
            f"{self.base_url}/v1/search",
            params={"q": query, "type": media_type, "limit": limit, "offset": offset},
            headers={"Authorization": f"Bearer {self.token}"},
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise ProviderHttpError(response.status, response.reason)

    async def get_track(self, track_id: str) -> dict:
        """Get track

        Args:
            track_id (str): Track ID

        Returns:
            dict: Track data
        """
        await self.authorize_client()
        cache = self.get_cache_file_path(f"tracks/{track_id}.json")
        cached = self.read_cached_data(cache)
        if cached is not None:
            return cached
        async with self.session.get(
            f"{self.base_url}/v1/tracks/{track_id}",
            headers={"Authorization": f"Bearer {self.token}"},
        ) as response:
            if response.status == 200:
                data = await response.json()
                self.write_data_to_cache(data, cache)
                return data
            else:
                raise ProviderHttpError(response.status, response.reason)

    async def get_album(self, album_id: str) -> dict:
        """Get album

        Args:
            album_id (str): Album ID

        Returns:
            dict: Album data
        """
        await self.authorize_client()
        cache = self.get_cache_file_path(f"albums/{album_id}.json")
        cached = self.read_cached_data(cache)
        if cached is not None:
            return cached
        async with self.session.get(
            f"{self.base_url}/v1/albums/{album_id}",
            headers={"Authorization": f"Bearer {self.token}"},
        ) as response:
            if response.status == 200:
                data = await response.json()
                self.write_data_to_cache(data, cache)
                return data
            else:
                raise ProviderHttpError(response.status, response.reason)

    async def get_artist(self, artist_id: str) -> dict:
        """Get artist

        Args:
            artist_id (str): Artist ID

        Returns:
            dict: Artist data
        """
        await self.authorize_client()
        cache = self.get_cache_file_path(f"artists/{artist_id}.json")
        cached = self.read_cached_data(cache)
        if cached is not None:
            return cached
        async with self.session.get(
            f"{self.base_url}/v1/artists/{artist_id}",
            headers={"Authorization": f"Bearer {self.token}"},
        ) as response:
            if response.status == 200:
                data = await response.json()
                self.write_data_to_cache(data, cache)
                return data
            else:
                raise ProviderHttpError(response.status, response.reason)

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
            with open(cache_file_path, "r") as cache_file:
                cache_data = json.load(cache_file)
                cache_age = time.time() - cache_data["timestamp"]
                if cache_age < self.cache_expiration_time:
                    return cache_data["data"]
        return None

    @staticmethod
    def write_data_to_cache(data, cache_file_path: str):
        """Write data to cache

        Args:
            data (any): Data to write
            cache_file_name (str): Cache file name
        """
        cache_data = {"timestamp": time.time(), "data": data}
        os.makedirs(os.path.dirname(cache_file_path), exist_ok=True)
        with open(cache_file_path, "w") as cache_file:
            json.dump(cache_data, cache_file)
