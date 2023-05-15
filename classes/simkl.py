"""Simkl API wrapper

This module is a wrapper for Simkl API, which is used to search for anime, shows, and movies."""

import json
import os
import time
from copy import deepcopy
from enum import Enum
from typing import List, Literal
from urllib.parse import quote
from dataclassy import dataclass

import aiohttp

from classes.excepts import ProviderHttpError, SimklTypeError
from modules.const import SIMKL_CLIENT_ID, simkl0rels, USER_AGENT


@dataclass(kwargs=True)
class SimklRelations:
    title: str | None = None
    simkl: int | None = None
    slug: str | None = None
    poster: str | None = None
    fanart: str | None = None
    anitype: Literal["tv", "movie", "special", "ova", "ona"] | str | None = None
    type: Literal["anime", "show", "movie"] | str | None = None
    allcin: str | int | None = None
    anfo: str | int | None = None
    anidb: str | int | None = None
    anilist: str | int | None = None
    animeplanet: str | int | None = None
    anisearch: str | int | None = None
    ann: str | int | None = None
    hulu: str | int | None = None
    imdb: str | None = None
    kitsu: str | int | None = None
    livechart: str | int | None = None
    mal: str | int | None = None
    netflix: str | int | None = None
    offjp: str | int | None = None
    tmdb: str | int | None = None
    tvdb: str | int | None = None
    tvdbslug: str | None = None
    wikien: str | int | None = None
    wikijp: str | int | None = None


class SimklMediaGenre(Enum):
    ACTION = "Action"
    ADVENTURE = "Adventure"
    ANIMATION = "Animation"
    COMEDY = "Comedy"
    CRIME = "Crime"
    DOCUMENTARY = "Documentary"
    DRAMA = "Drama"
    FANTASY = "Fantasy"
    HISTORY = "History"
    HORROR = "Horror"
    MYSTERY = "Mystery"
    ROMANCE = "Romance"
    SCIENCE_FICTION = "Science Fiction"
    THRILLER = "Thriller"
    WAR = "War"
    WESTERN = "Western"


class SimklMovieGenre(Enum):
    ACTION = SimklMediaGenre.ACTION.value
    ADVENTURE = SimklMediaGenre.ADVENTURE.value
    ANIMATION = SimklMediaGenre.ANIMATION.value
    COMEDY = SimklMediaGenre.COMEDY.value
    CRIME = SimklMediaGenre.CRIME.value
    DOCUMENTARY = SimklMediaGenre.DOCUMENTARY.value
    DRAMA = SimklMediaGenre.DRAMA.value
    EROTICA = "Erotica"
    FAMILY = "Family"
    FANTASY = SimklMediaGenre.FANTASY.value
    FOREIGN = "Foreign"
    HISTORY = "History"
    MUSIC = "Music"
    MYSTERY = SimklMediaGenre.MYSTERY.value
    ROMANCE = SimklMediaGenre.ROMANCE.value
    SCIENCE_FICTION = SimklMediaGenre.SCIENCE_FICTION.value
    THRILLER = SimklMediaGenre.THRILLER.value
    TV_MOVIE = "TV Movie"
    WAR = SimklMediaGenre.WAR.value
    WESTERN = SimklMediaGenre.WESTERN.value


class SimklTvGenre(Enum):
    ACTION = SimklMediaGenre.ACTION.value
    ADVENTURE = SimklMediaGenre.ADVENTURE.value
    ANIMATION = SimklMediaGenre.ANIMATION.value
    AWARDS_SHOW = "Awards Show"
    CHILDREN = "Children's"
    COMEDY = SimklMediaGenre.COMEDY.value
    CRIME = SimklMediaGenre.CRIME.value
    DOCUMENTARY = SimklMediaGenre.DOCUMENTARY.value
    DRAMA = SimklMediaGenre.DRAMA.value
    EROTICA = "Erotica"
    FAMILY = "Family"
    FANTASY = SimklMediaGenre.FANTASY.value
    FOOD = "Food"
    GAME_SHOW = "Game Show"
    HISTORY = SimklMediaGenre.HISTORY.value
    HOME_AND_GARDEN = "Home and Garden"
    HORROR = SimklMediaGenre.HORROR.value
    INDIE = "Indie"
    KOREAN_DRAMA = "Korean Drama"
    MARTIAL_ARTS = "Martial Arts"
    MINI_SERIES = "Mini-series"
    MUSICAL = "Musical"
    MYSTERY = SimklMediaGenre.MYSTERY.value
    NEWS = "News"
    PODCAST = "Podcast"
    REALITY = "Reality"
    ROMANCE = SimklMediaGenre.ROMANCE.value
    SCIENCE_FICTION = SimklMediaGenre.SCIENCE_FICTION.value
    SOAP_OPERA = "Soap Opera"
    SPECIAL_INTEREST = "Special Interest"
    SPORTS = "Sports"
    SUSPENSE = "Suspense"
    TALK_SHOW = "Talk Show"
    THRILLER = SimklMediaGenre.THRILLER.value
    TRAVEL = "Travel"
    WAR = SimklMediaGenre.WAR.value
    WESTERN = SimklMediaGenre.WESTERN.value


class SimklAnimeGenre(Enum):
    ACTION = SimklMediaGenre.ACTION.value
    ADVENTURE = SimklMediaGenre.ADVENTURE.value
    CARS = "Cars"
    COMEDY = SimklMediaGenre.COMEDY.value
    DEMENTIA = "Dementia"
    DEMONS = "Demons"
    DRAMA = SimklMediaGenre.DRAMA.value
    ECCHI = "Ecchi"
    FANTASY = SimklMediaGenre.FANTASY.value
    GAME = "Game"
    HAREM = "Harem"
    HISTORICAL = "Historical"
    HORROR = SimklMediaGenre.HORROR.value
    JOSEI = "Josei"
    KIDS = "Kids"
    MAGIC = "Magic"
    MARTIAL_ARTS = "Martial Arts"
    MECHA = "Mecha"
    MILITARY = "Military"
    MUSIC = "Music"
    MYSTERY = SimklMediaGenre.MYSTERY.value
    PARODY = "Parody"
    POLICE = "Police"
    PSYCHOLOGICAL = "Psychological"
    ROMANCE = SimklMediaGenre.ROMANCE.value
    SAMURAI = "Samurai"
    SCHOOL = "School"
    SCI_FI = "Sci-Fi"
    SEINEN = "Seinen"
    SHOUJO = "Shoujo"
    SHOUJO_AI = "Shoujo Ai"
    SHOUNEN = "Shounen"
    SHOUNEN_AI = "Shounen Ai"
    SLICE_OF_LIFE = "Slice of Life"
    SPACE = "Space"
    SPORTS = "Sports"
    SUPER_POWER = "Super Power"
    SUPERNATURAL = "Supernatural"
    THRILLER = SimklMediaGenre.THRILLER.value
    VAMPIRE = "Vampire"
    YAOI = "Yaoi"
    YURI = "Yuri"


class SimklMediaTypes(Enum):
    """Media types supported by Simkl API"""

    ANIME = "anime"
    MOVIE = "movie"
    SHOW = TV = "tv"


class Simkl:
    """Simkl API wrapper

    This module is a wrapper for Simkl API, which is used to search for anime, shows, and movies.
    """

    def __init__(self, client_id: str = SIMKL_CLIENT_ID):
        """Initialize the Simkl API wrapper

        Args:
            client_id (str): Client ID for SIMKL API, defaults to SIMKL_CLIENT_ID
        """
        self.client_id = client_id
        if client_id is None:
            raise ProviderHttpError(
                "Unauthorized, please fill Client ID before using this module", 401
            )
        self.base_url = "https://api.simkl.com"
        self.params = {"client_id": self.client_id}
        self.session = None
        self.cache_directory = "cache/simkl"
        self.cache_expiration_time = 86400  # 1 day in seconds

    async def __aenter__(self):
        """Enter the async context manager"""
        self.session = aiohttp.ClientSession(headers={"User-Agent": USER_AGENT})
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the async context manager"""
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

    async def search_by_id(
        self,
        provider: Provider | str,
        id: int | str,
        media_type: TmdbMediaTypes | str | None = None,
    ) -> dict:
        """Search by ID

        Args:
            provider (Provider | str): Provider to search
            id (int): ID of the provider
            media_type (TmdbMediaTypes | str | None, optional): Media type of the title, must be SHOW or MOVIE. Defaults to None

        Raises:
            SimklTypeError: If provider is TMDB and media_type is not provided
            ProviderHttpError: If response status is not 200

        Returns:
            dict: Response from Simkl API
        """
        params = deepcopy(self.params)
        if isinstance(provider, self.Provider):
            provider = provider.value
        if provider == self.Provider.TMDB and not media_type:
            raise SimklTypeError(
                "MediaType is required when using TMDB provider",
                "TmdbMediaTypeRequired",
            )
        params[f"{provider}"] = id
        async with self.session.get(
            f"{self.base_url}/search/id", params=params
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data
            error_message = await response.text()
            raise ProviderHttpError(error_message, response.status)

    async def search_by_title(
        self,
        title: str,
        media_type: SimklMediaTypes | str,
        page: int = 1,
        limit: int = 10,
        extended: bool = False,
    ) -> dict:
        """Search by title

        Args:
            title (str): Title to search
            media_type (SimklMediaTypes | str): Media type of the title, must be ANIME, MOVIE or TV
            page (int, optional): Page number. Defaults to 1.
            limit (int, optional): Limit of results per page. Defaults to 10.
            extended (bool, optional): Get extended info. Defaults to False.

        Raises:
            ProviderHttpError: If response status is not 200

        Returns:
            dict: Response from Simkl API
        """
        params = deepcopy(self.params)
        params["q"] = quote(title)
        if extended:
            params["extended"] = "full"
        params["page"] = page
        params["limit"] = limit
        async with self.session.get(
            f"{self.base_url}/search/{media_type}", params=params
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data
            error_message = await response.text()
            raise ProviderHttpError(error_message, response.status)

    async def get_show(self, id: int | str) -> dict:
        """Get show by ID

        Args:
            id (int): Show ID on SIMKL or IMDB
            extended (bool, optional): Get extended info. Defaults to False.

        Raises:
            ProviderHttpError: If response status is not 200

        Returns:
            dict: Response from Simkl API
        """
        cache_file_path = self.get_cache_file_path(f"show/{id}.json")
        cached_data = self.read_cached_data(cache_file_path)
        if cached_data is not None:
            return cached_data
        params = deepcopy(self.params)
        params["extended"] = "full"
        async with self.session.get(
            f"{self.base_url}/tv/{id}", params=params
        ) as response:
            if response.status == 200:
                data = await response.json()
                self.write_data_to_cache(data, cache_file_path)
                return data
            error_message = await response.text()
            raise ProviderHttpError(error_message, response.status)

    async def get_movie(self, id: int | str) -> dict:
        """Get movie by ID

        Args:
            id (int): Movie ID on SIMKL or IMDB
            extended (bool, optional): Get extended info. Defaults to False.

        Raises:
            ProviderHttpError: If response status is not 200

        Returns:
            dict: Response from Simkl API
        """
        cache_file_path = self.get_cache_file_path(f"movie/{id}.json")
        cached_data = self.read_cached_data(cache_file_path)
        if cached_data is not None:
            return cached_data
        params = deepcopy(self.params)
        params["extended"] = "full"
        async with self.session.get(
            f"{self.base_url}/movies/{id}", params=params
        ) as response:
            if response.status == 200:
                data = await response.json()
                self.write_data_to_cache(data, cache_file_path)
                return data
            error_message = await response.text()
            raise ProviderHttpError(error_message, response.status)

    async def get_anime(self, id: int | str) -> dict:
        """Get anime by ID

        Args:
            id (int): Anime ID on SIMKL or IMDB
            extended (bool, optional): Get extended info. Defaults to False.

        Raises:
            ProviderHttpError: If response status is not 200

        Returns:
            dict: Response from Simkl API
        """
        cache_file_path = self.get_cache_file_path(f"anime/{id}.json")
        cached_data = self.read_cached_data(cache_file_path)
        if cached_data is not None:
            return cached_data
        params = deepcopy(self.params)
        params["extended"] = "full"
        async with self.session.get(
            f"{self.base_url}/anime/{id}", params=params
        ) as response:
            if response.status == 200:
                data = await response.json()
                self.write_data_to_cache(data, cache_file_path)
                return data
            error_message = await response.text()
            raise ProviderHttpError(error_message, response.status)

    async def get_random_title(
        self,
        media_type: SimklMediaTypes | str,
        genre: SimklMediaGenre
        | SimklMovieGenre
        | SimklTvGenre
        | SimklAnimeGenre
        | str
        | None = None,
        year_from: int | None = None,
        year_to: int | None = None,
        rating_limit: int | None = None,
        rating_from: int = 0,
        rating_to: int = 10,
    ) -> dict | List[dict] | None:
        """Get random title, based on filters

        Args:
            media_type (SimklMediaTypes | str): Media type of the title, must be ANIME, MOVIE or TV
            genre (SimklMediaGenre | SimklMovieGenre | SimklTvGenre | SimklAnimeGenre | str | None, optional): Genre of the title. Defaults to None.
            year_from (int | None, optional): Year from. Defaults to None.
            year_to (int | None, optional): Year to. Defaults to None.
            rating_limit (int | None, optional): Rating limit. Defaults to None.
            rating_from (int, optional): Rating from. Defaults to 0.
            rating_to (int, optional): Rating to. Defaults to 10.

        Raises:
            ProviderHttpError: If response status is not 200

        Returns:
            dict | List[dict] | None: Response from Simkl API
        """
        params = self.params
        if isinstance(media_type, SimklMediaTypes):
            media_type = media_type.value
        if media_type == "show":
            media_type = "tv"
        params["type"] = media_type
        if genre:
            if isinstance(genre, str):
                match media_type:
                    case "anime":
                        genre = SimklAnimeGenre(genre)
                    case "movie":
                        genre = SimklMovieGenre(genre)
                    case "tv":
                        genre = SimklTvGenre(genre)
            params["genre"] = genre.value
        if year_from:
            params["year_from"] = year_from
        if year_to:
            params["year_to"] = year_to
        if rating_limit:
            params["rating_limit"] = rating_limit
        if rating_from:
            params["rating_from"] = rating_from
        if rating_to:
            params["rating_to"] = rating_to
        async with self.session.get(
            f"{self.base_url}/search/random/", params=params
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data
            error_message = await response.text()
            raise ProviderHttpError(error_message, response.status)

    async def get_title_ids(self, id: int, media_type: SimklMediaTypes | Literal["anime", "movie", "tv"]) -> SimklRelations:
        """Get IDs of the title

        Args:
            id (int): ID of the title
            media_type (SimklMediaTypes | Literal["anime", "movie", "tv"]): Media type of the title, must be ANIME, MOVIE or TV

        Raises:
            ProviderHttpError: If response status is not 200

        Returns:
            SimklRelations: Response from Simkl API
        """
        if isinstance(media_type, SimklMediaTypes):
            media_type = media_type.value
        cache_file_path = self.get_cache_file_path(f"ids/{media_type}/{id}.json")
        cached_data = self.read_cached_data(cache_file_path)
        if cached_data is not None:
            return SimklRelations(**cached_data)
        if media_type == "anime":
            async with Simkl(self.client_id) as simkl:
                data = await simkl.get_anime(id)
        elif media_type == "movie":
            async with Simkl(self.client_id) as simkl:
                data = await simkl.get_movie(id)
        elif media_type == "tv":
            async with Simkl(self.client_id) as simkl:
                data = await simkl.get_show(id)
        else:
            raise SimklTypeError(f"You've might entered false media_type", SimklMediaTypes)

        mids = {**simkl0rels, **data.get("ids", {})}
        for k, v in mids.items():
            if k in [
                "title",
                "slug",
                "animeplanet",
                "tvdbslug",
                "crunchyrolll",
                "fb",
                "instagram",
                "twitter",
                "wikien",
                "wikijp",
            ]:
                continue
            if isinstance(v, str) and v.isdigit():
                mids[k] = int(v)
        keys = ["title", "poster", "fanart", "anime_type", "type"]
        for k in keys:
            if k == "anime_type":
                mids["anitype"] = data.get(k, None)
                continue
            mids[k] = data.get(k, None)
        self.write_data_to_cache(mids, cache_file_path)
        return SimklRelations(**mids)

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
            data (any): Data to write to cache
            cache_file_name (str): Cache file name
        """
        cache_data = {"timestamp": time.time(), "data": data}
        os.makedirs(os.path.dirname(cache_file_path), exist_ok=True)
        with open(cache_file_path, "w") as cache_file:
            json.dump(cache_data, cache_file)


__all__ = ["Simkl"]
