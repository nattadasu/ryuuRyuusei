"""Simkl API wrapper

This module is a wrapper for Simkl API, which is used to search for anime, shows, and movies."""

import aiohttp
from urllib.parse import quote
import os
import time
import json
from enum import Enum

from classes.excepts import ProviderHttpError, SimklTypeError
from modules.const import simkl0rels, SIMKL_CLIENT_ID


class Simkl:
    """Simkl API wrapper

    This module is a wrapper for Simkl API, which is used to search for anime, shows, and movies."""

    def __init__(self, client_id: str = SIMKL_CLIENT_ID):
        self.client_id = client_id
        if client_id is None:
            raise ProviderHttpError(
                "Unauthorized, please fill Client ID before using this module", 401)
        self.base_url = "https://api.simkl.com"
        self.params = {"client_id": self.client_id}
        self.session = None
        self.cache_directory = 'cache/simkl'
        self.cache_expiration_time = 86400 # 1 day in seconds

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.session.close()

    async def close(self) -> None:
        """Close the session"""
        await self.session.close()

    class Provider(Enum):
        """Providers supported by Simkl API"""
        ANIDB = "anidb"
        ANILIST = AL = "anilist"
        ANIMEPLANET = AP = "animeplanet"
        ANISEARCH = AS = "anisearch"
        CRUNCHYROLL = CR = "crunchyroll"
        HULU = "hulu"
        IMDB = "imdb"
        KITSU = "kitsu"
        LIVECHART = "livechart"
        MYANIMELIST = MAL = "mal"
        NETFLIX = "netflix"
        TMDB = "tmdb"
        TVDB = "tvdb"

    class TmdbMediaTypes(Enum):
        """Media types required to reverse lookup from TMDB ID"""
        SHOW = "show"
        MOVIE = "movie"

    class MediaTypes(Enum):
        """Media types supported by Simkl API"""
        ANIME = "anime"
        MOVIE = "movie"
        TV = "tv"

    async def search_by_id(self, provider: Provider, id: int, media_type: TmdbMediaTypes | str | None = None):
        """Search by ID

        Args:
            provider (Provider): Provider to search
            id (int): ID of the provider
            media_type (TmdbMediaTypes, optional): Media type of the title, must be SHOW or MOVIE. Defaults to None."""
        params = self.params
        if provider == self.Provider.TMDB and not media_type:
            raise SimklTypeError(
                "MediaType is required when using TMDB provider", "TmdbMediaTypeRequired")
        params[f"{provider}"] = id
        async with self.session.get(f"{self.base_url}/search/{provider}/{id}", params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                error_message = await response.text()
                raise ProviderHttpError(error_message, response.status)

    async def search_by_title(
        self,
        title: str,
        media_type: MediaTypes | str,
        page: int = 1,
        limit: int = 10,
        extended: bool = False,
    ) -> dict:
        """Search by title

        Args:
            title (str): Title to search
            media_type (MediaTypes): Media type of the title, must be ANIME, MOVIE or TV
            page (int, optional): Page number. Defaults to 1.
            limit (int, optional): Limit of results per page. Defaults to 10.
            extended (bool, optional): Get extended info. Defaults to False.
        """
        params = self.params
        params["q"] = quote(title)
        if extended:
            params["extended"] = "full"
        params["page"] = page
        params["limit"] = limit
        async with self.session.get(f"{self.base_url}/search/{media_type}", params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                error_message = await response.text()
                raise ProviderHttpError(error_message, response.status)

    async def get_show(self, id: int) -> dict:
        """Get show by ID

        Args:
            id (int): Show ID on SIMKL or IMDB
            extended (bool, optional): Get extended info. Defaults to False.
        """
        cache_file_path = self.get_cache_file_path(f'show/{id}.json')
        cached_data = self.read_cached_data(cache_file_path)
        if cached_data is not None:
            return cached_data
        params = self.params
        params["extended"] = "full"
        async with self.session.get(f"{self.base_url}/tv/{id}", params=params) as response:
            if response.status == 200:
                data = await response.json()
                self.write_data_to_cache(cache_file_path, data)
                return data
            else:
                error_message = await response.text()
                raise ProviderHttpError(error_message, response.status)

    async def get_movie(self, id: int) -> dict:
        """Get movie by ID

        Args:
            id (int): Movie ID on SIMKL or IMDB
            extended (bool, optional): Get extended info. Defaults to False.
        """
        cache_file_path = self.get_cache_file_path(f'movie/{id}.json')
        cached_data = self.read_cached_data(cache_file_path)
        if cached_data is not None:
            return cached_data
        params = self.params
        params["extended"] = "full"
        async with self.session.get(f"{self.base_url}/movies/{id}", params=params) as response:
            if response.status == 200:
                data = await response.json()
                self.write_data_to_cache(cache_file_path, data)
                return data
            else:
                error_message = await response.text()
                raise ProviderHttpError(error_message, response.status)

    async def get_anime(self, id: int) -> dict:
        """Get anime by ID

        Args:
            id (int): Anime ID on SIMKL or IMDB
            extended (bool, optional): Get extended info. Defaults to False.
        """
        cache_file_path = self.get_cache_file_path(f'anime/{id}.json')
        cached_data = self.read_cached_data(cache_file_path)
        if cached_data is not None:
            return cached_data
        params = self.params
        params["extended"] = "full"
        async with self.session.get(f"{self.base_url}/anime/{id}", params=params) as response:
            if response.status == 200:
                data = await response.json()
                self.write_data_to_cache(cache_file_path, data)
                return data
            else:
                error_message = await response.text()
                raise ProviderHttpError(error_message, response.status)

    async def get_title_ids(self, id: int, media_type: MediaTypes | str) -> dict:
        """Get IDs of the title

        Args:
            id (int): ID of the title
            media_type (MediaTypes): Media type of the title, must be ANIME, MOVIE or TV
        """
        cache_file_path = self.get_cache_file_path(f'ids/{media_type}/{id}.json')
        cached_data = self.read_cached_data(cache_file_path)
        if cached_data is not None:
            return cached_data
        if media_type == "anime":
            async with Simkl(self.client_id) as simkl:
                data = await simkl.get_anime(id)
        elif media_type == "movie":
            async with Simkl(self.client_id) as simkl:
                data = await simkl.get_movie(id)
        elif media_type == "tv":
            async with Simkl(self.client_id) as simkl:
                data = await simkl.get_show(id)

        mids = {**simkl0rels, **data.get("ids", {})}
        for k, v in mids.items():
            if k in ["title", "slug", "animeplanet", "tvdbslug", "crunchyrolll", "fb", "instagram", "twitter", "wikien", "wikijp"]:
                continue
            if isinstance(v, str) and v.isdigit():
                mids[k] = int(v)
        keys = [
            'title', 'poster', 'fanart', 'anime_type', 'type'
        ]
        for k in keys:
            if k == 'anime_type':
                mids['anitype'] = data.get(k, None)
                continue
            mids[k] = data.get(k, None)
        self.write_data_to_cache(cache_file_path, mids)
        return mids

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

__all__ = ['Simkl']
