"""AniList Asynchronous API Wrapper"""
import json
import os
import time
from enum import Enum

import aiohttp

from classes.excepts import ProviderHttpError, ProviderTypeError


class AniList:
    """AniList Asynchronous API Wrapper"""

    def __init__(self):
        self.base_url = "https://graphql.anilist.co"
        self.session = None
        self.cache_directory = 'cache/anilist'
        self.cache_expiration_time = 86400  # 1 day in seconds

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    async def close(self) -> None:
        await self.session.close()

    class MediaType(Enum):
        """Media type enum for AniList"""
        ANIME = "ANIME"
        MANGA = "MANGA"

    async def nsfwCheck(self, media_id: int, media_type: str | MediaType = "ANIME"):
        """Check if the media is NSFW"""
        self.cache_expiration_time = 604800
        if isinstance(media_type, self.MediaType):
            media_type = media_type.value
        cache_file_path = self.get_cache_file_path(
            f'nsfw/{media_type.lower()}/{id}.json')
        cached_data = self.read_cached_data(cache_file_path)
        if cached_data is not None:
            return cached_data
        if isinstance(media_type, str):
            media_type = media_type.upper()
        query = f"""query {{
    Media(id: {media_id}, type: {media_type}) {{
        id
        isAdult
    }}
}}"""
        async with self.session.post(self.base_url, json={"query": query}) as response:
            if response.status == 200:
                data = await response.json()
                self.write_data_to_cache(
                    cache_file_path, data["data"]["Media"]["isAdult"])
                return data["data"]["Media"]["isAdult"]
            else:
                error_message = await response.text()
                raise ProviderHttpError(error_message, response.status)

    async def anime(self, media_id: int):
        """Get anime information by its ID"""
        cache_file_path = self.get_cache_file_path(f'anime/{media_id}.json')
        cached_data = self.read_cached_data(cache_file_path)
        if cached_data is not None:
            return cached_data
        gqlquery = f"""query {{
    Media(id: {media_id}, type: ANIME) {{
        id
        idMal
        title {{
            romaji
            english
            native
        }}
        isAdult
        description(asHtml: false)
        synonyms
        format
        startDate {{
            year
            month
            day
        }}
        endDate {{
            year
            month
            day
        }}
        status
        chapters
        volumes
        coverImage {{
            large
            extraLarge
        }}
        bannerImage
        genres
        tags {{
            name
            isMediaSpoiler
        }}
        averageScore
        stats {{
            scoreDistribution {{
                score
                amount
            }}
        }}
        trailer {{
            id
            site
        }}
    }}
}}"""
        async with self.session.post(self.base_url, json={"query": gqlquery}) as response:
            if response.status == 200:
                data = await response.json()
                self.write_data_to_cache(
                    cache_file_path, data["data"]["Media"])
                return data["data"]["Media"]
            else:
                error_message = await response.text()
                raise ProviderHttpError(error_message, response.status)

    async def manga(self, media_id: int):
        """Get manga information by its ID"""
        cache_file_path = self.get_cache_file_path(f'manga/{media_id}.json')
        cached_data = self.read_cached_data(cache_file_path)
        if cached_data is not None:
            return cached_data
        gqlquery = f"""query {{
    Media(id: {media_id}, type: MANGA) {{
        id
        idMal
        title {{
            romaji
            english
            native
        }}
        isAdult
        description(asHtml: false)
        synonyms
        format
        startDate {{
            year
            month
            day
        }}
        endDate {{
            year
            month
            day
        }}
        status
        chapters
        volumes
        coverImage {{
            extraLarge
            large
        }}
        bannerImage
        genres
        tags {{
            name
            isMediaSpoiler
        }}
        averageScore
        stats {{
            scoreDistribution {{
                score
                amount
            }}
        }}
        trailer {{
            id
            site
        }}
    }}
}}"""
        async with self.session.post(self.base_url, json={"query": gqlquery}) as response:
            if response.status == 200:
                data = await response.json()
                self.write_data_to_cache(
                    cache_file_path, data["data"]["Media"])
                return data["data"]["Media"]
            else:
                error_message = await response.text()
                raise ProviderHttpError(error_message, response.status)

    async def search_media(self, query: str, limit: int = 10, media_type: str | MediaType = "MANGA"):
        """Search anime by its title"""
        if limit > 10:
            raise ProviderTypeError(
                "limit must be less than or equal to 10", "int")
        if isinstance(media_type, self.MediaType):
            media_type = media_type.value
        gqlquery = f"""query ($search: String, $mediaType: MediaType, $limit: Int) {{
    Page(page: 1, perPage: $limit) {{
        results: media(search: $search, type: $mediaType) {{
            id
            idMal
            title {{
                romaji
                english
                native
            }}
            format
            isAdult
            startDate {{
                year
            }}
            season
        }}
    }}
}}"""
        variables = {
            "search": query,
            "mediaType": media_type,
            "limit": limit,
        }
        async with self.session.post(self.base_url, json={"query": gqlquery, "variables": variables}) as response:
            if response.status == 200:
                data = await response.json()
                return data["data"]["Page"]["results"]
            else:
                error_message = await response.text()
                raise ProviderHttpError(error_message, response.status)

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


__all__ = ["AniList"]
