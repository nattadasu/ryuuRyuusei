"""
Simkl API wrapper

This module is a wrapper for Simkl API, which is used to search for anime, shows, and movies.
"""

from copy import deepcopy
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, List, Literal
from urllib.parse import quote

import aiohttp

from classes.cache import Caching
from classes.excepts import ProviderHttpError, SimklTypeError
from modules.const import SIMKL_CLIENT_ID, USER_AGENT

Cache = Caching("cache/simkl", 86400)


@dataclass
class SimklRelations:
    """Simkl Relations dataclass"""

    title: str | None = None
    """Title of the anime, show, or movie"""
    simkl: int | None = None
    """Simkl ID"""
    slug: str | None = None
    """Simkl slug"""
    poster: str | None = None
    """Simkl poster path"""
    fanart: str | None = None
    """Simkl fanart path"""
    anitype: Literal["tv", "movie", "special", "ova", "ona"] | None = None
    """Anime type"""
    type: Literal["anime", "show", "movie"] | None = None
    """Title type"""
    allcin: str | int | None = None
    """Allcinema ID"""
    anfo: str | int | None = None
    """Aninfo ID"""
    anidb: str | int | None = None
    """AniDB ID"""
    anilist: str | int | None = None
    """AniList ID"""
    animeplanet: str | int | None = None
    """Anime-Planet ID"""
    anisearch: str | int | None = None
    """AniSearch ID"""
    ann: str | int | None = None
    """Anime News Network ID"""
    hulu: str | int | None = None
    """Hulu ID"""
    imdb: str | None = None
    """IMDb ID"""
    kitsu: str | int | None = None
    """Kitsu ID"""
    livechart: str | int | None = None
    """LiveChart ID"""
    mal: str | int | None = None
    """MyAnimeList ID"""
    netflix: str | int | None = None
    """Netflix ID"""
    offjp: str | int | None = None
    """Offical Japanese website ID"""
    tmdb: str | int | None = None
    """TheMovieDb ID"""
    tvdb: str | int | None = None
    """TheTVDb ID"""
    tvdbslug: str | None = None
    """TheTVDb slug"""
    tvdbmslug: str | None = None
    """TheTVDb movie slug"""
    wikien: str | int | None = None
    """English Wikipedia ID"""
    wikijp: str | int | None = None
    """Japanese Wikipedia ID"""

    def to_dict(self) -> dict[str, Any]:
        """Convert the dataclass to a dictionary"""
        return asdict(self)


class SimklMediaGenre(Enum):
    """Simkl Media Genre enum"""

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
    """Simkl Movie Genre enum"""

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
    """Simkl TV Genre enum"""

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
    """Simkl Anime Genre enum"""

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
    """
    Simkl API wrapper

    This module is a wrapper for Simkl API, which is used to search for anime, shows, and movies.
    """

    def __init__(self, client_id: str = SIMKL_CLIENT_ID):
        """
        Initialize the Simkl API wrapper

        Args:
            client_id (str): Client ID for SIMKL API, defaults to SIMKL_CLIENT_ID
        """
        self.client_id = client_id
        if client_id == "":
            raise ProviderHttpError(
                "Unauthorized, please fill Client ID before using this module", 401)
        self.base_url = "https://api.simkl.com"
        self.params = {"client_id": self.client_id}
        self.session = aiohttp.ClientSession(
            headers={"User-Agent": USER_AGENT})

    async def __aenter__(self):
        """Enter the async context manager"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
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
        media_id: int | str,
        media_type: TmdbMediaTypes | Literal["show", "movie"] | None = None,
    ) -> dict[str, Any]:
        """
        Search by ID

        Args:
            provider (Provider | str): Provider to search
            media_id (int): ID of the provider
            media_type (TmdbMediaTypes | Literal["show", "movie"] | None, optional): Media type of the title, must be SHOW or MOVIE. Defaults to None

        Raises:
            SimklTypeError: If provider is TMDB and media_type is not provided
            ProviderHttpError: If response status is not 200

        Returns:
            dict: Response from Simkl API
        """
        params: dict[str, Any] = deepcopy(self.params)
        if isinstance(provider, self.Provider):
            provider = provider.value
        if provider == self.Provider.TMDB and not media_type:
            raise SimklTypeError(
                "MediaType is required when using TMDB provider",
                "TmdbMediaTypeRequired",
            )
        params[f"{provider}"] = media_id
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
    ) -> list[dict[str, Any]]:
        """
        Search by title

        Args:
            title (str): Title to search
            media_type (SimklMediaTypes | str): Media type of the title, must be ANIME, MOVIE or TV
            page (int, optional): Page number. Defaults to 1.
            limit (int, optional): Limit of results per page. Defaults to 10.
            extended (bool, optional): Get extended info. Defaults to False.

        Raises:
            ProviderHttpError: If response status is not 200

        Returns:
            list[dict[str, Any]]: Response from Simkl API
        """
        params: dict[str, Any] = deepcopy(self.params)
        params["q"] = quote(title)
        if extended:
            params["extended"] = "full"
        params["page"] = page
        params["limit"] = limit
        media_type = media_type.value if isinstance(
            media_type, Enum) else media_type
        async with self.session.get(
            f"{self.base_url}/search/{media_type}", params=params
        ) as response:
            if response.status == 200:
                data = await response.json()
                return data
            error_message = await response.text()
            raise ProviderHttpError(error_message, response.status)

    async def get_show(self, media_id: int | str) -> dict[str, Any]:
        """
        Get show by ID

        Args:
            media_id (int | str): Show ID on SIMKL or IMDB
            extended (bool, optional): Get extended info. Defaults to False.

        Raises:
            ProviderHttpError: If response status is not 200

        Returns:
            dict: Response from Simkl API
        """
        cache_file_path = Cache.get_cache_file_path(f"show/{media_id}.json")
        cached_data = Cache.read_cached_data(cache_file_path)
        if cached_data is not None:
            return cached_data
        params = deepcopy(self.params)
        params["extended"] = "full"
        async with self.session.get(
            f"{self.base_url}/tv/{media_id}", params=params
        ) as response:
            if response.status == 200:
                data = await response.json()
                Cache.write_data_to_cache(data, cache_file_path)
                return data
            error_message = await response.text()
            raise ProviderHttpError(error_message, response.status)

    async def get_movie(self, media_id: int | str) -> dict[str, Any]:
        """
        Get movie by ID

        Args:
            media_id (int | str): Movie ID on SIMKL or IMDB
            extended (bool, optional): Get extended info. Defaults to False.

        Raises:
            ProviderHttpError: If response status is not 200

        Returns:
            dict: Response from Simkl API
        """
        cache_file_path = Cache.get_cache_file_path(f"movie/{media_id}.json")
        cached_data = Cache.read_cached_data(cache_file_path)
        if cached_data is not None:
            return cached_data
        params = deepcopy(self.params)
        params["extended"] = "full"
        async with self.session.get(
            f"{self.base_url}/movies/{media_id}", params=params
        ) as response:
            if response.status == 200:
                data = await response.json()
                Cache.write_data_to_cache(data, cache_file_path)
                return data
            error_message = await response.text()
            raise ProviderHttpError(error_message, response.status)

    async def get_anime(self, media_id: int | str) -> dict[str, Any]:
        """
        Get anime by ID

        Args:
            media_id (int | str): Anime ID on SIMKL or IMDB
            extended (bool, optional): Get extended info. Defaults to False.

        Raises:
            ProviderHttpError: If response status is not 200

        Returns:
            dict: Response from Simkl API
        """
        cache_file_path = Cache.get_cache_file_path(f"anime/{media_id}.json")
        cached_data = Cache.read_cached_data(cache_file_path)
        if cached_data is not None:
            return cached_data
        params = deepcopy(self.params)
        params["extended"] = "full"
        async with self.session.get(
            f"{self.base_url}/anime/{media_id}", params=params
        ) as response:
            if response.status == 200:
                data = await response.json()
                Cache.write_data_to_cache(data, cache_file_path)
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
    ) -> dict[str, Any] | List[dict[str, Any]] | None:
        """
        Get random title, based on filters

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
        params: dict[str, Any] = deepcopy(self.params)
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
                    case _:
                        raise ValueError("Invalid media type")
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

    async def get_title_ids(
        self,
        media_id: int,
        media_type: SimklMediaTypes | Literal["anime", "movie", "tv"],
    ) -> SimklRelations:
        """
        Get IDs of the title

        Args:
            media_id (int): ID of the title
            media_type (SimklMediaTypes | Literal["anime", "movie", "tv"]): Media type of the title, must be ANIME, MOVIE or TV

        Raises:
            ProviderHttpError: If response status is not 200

        Returns:
            SimklRelations: Response from Simkl API
        """
        if isinstance(media_type, SimklMediaTypes):
            media_type = media_type.value
        cache_file_path = Cache.get_cache_file_path(
            f"ids/{media_type}/{media_id}.json")
        cached_data = Cache.read_cached_data(cache_file_path)
        if cached_data is not None:
            cached_data = SimklRelations(
                title=cached_data["title"],
                slug=cached_data["slug"],
                poster=cached_data["poster"],
                fanart=cached_data["fanart"],
                anitype=cached_data["anitype"],
                type=cached_data["type"],
                allcin=cached_data["allcin"],
                anfo=cached_data["anfo"],
                anidb=cached_data["anidb"],
                anilist=cached_data["anilist"],
                animeplanet=cached_data["animeplanet"],
                anisearch=cached_data["anisearch"],
                ann=cached_data["ann"],
                hulu=cached_data["hulu"],
                imdb=cached_data["imdb"],
                kitsu=cached_data["kitsu"],
                livechart=cached_data["livechart"],
                mal=cached_data["mal"],
                netflix=cached_data["netflix"],
                offjp=cached_data["offjp"],
                simkl=cached_data["simkl"],
                tmdb=cached_data["tmdb"],
                tvdb=cached_data["tvdb"],
                tvdbslug=cached_data["tvdbslug"],
                tvdbmslug=cached_data["tvdbmslug"],
                wikien=cached_data["wikien"],
                wikijp=cached_data["wikijp"],
            )
            return cached_data
        if media_type == "anime":
            async with Simkl(self.client_id) as simkl:
                data = await simkl.get_anime(media_id)
        elif media_type == "movie":
            async with Simkl(self.client_id) as simkl:
                data = await simkl.get_movie(media_id)
        elif media_type == "tv":
            async with Simkl(self.client_id) as simkl:
                data = await simkl.get_show(media_id)
        else:
            raise SimklTypeError(
                "You've might entered false media_type", SimklMediaTypes
            )

        nullrels = asdict(SimklRelations())

        mids = {**nullrels, **data.get("ids", {})}
        for key, value in mids.items():
            if key in [
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
            if isinstance(value, str) and value.isdigit():
                mids[key] = int(value)
        keys = ["title", "poster", "fanart", "anime_type", "type"]
        for key in keys:
            if key == "anime_type":
                mids["anitype"] = data.get(key, None)
                continue
            mids[key] = data.get(key, None)
        Cache.write_data_to_cache(mids, cache_file_path)
        relations = SimklRelations(
            title=mids["title"],
            slug=mids["slug"],
            poster=mids["poster"],
            fanart=mids["fanart"],
            anitype=mids["anitype"],
            type=mids["type"],
            allcin=mids["allcin"],
            anfo=mids["anfo"],
            anidb=mids["anidb"],
            anilist=mids["anilist"],
            animeplanet=mids["animeplanet"],
            anisearch=mids["anisearch"],
            ann=mids["ann"],
            hulu=mids["hulu"],
            imdb=mids["imdb"],
            kitsu=mids["kitsu"],
            livechart=mids["livechart"],
            mal=mids["mal"],
            netflix=mids["netflix"],
            offjp=mids["offjp"],
            simkl=mids["simkl"],
            tmdb=mids["tmdb"],
            tvdb=mids["tvdb"],
            tvdbmslug=mids["tvdbmslug"],
            tvdbslug=mids["tvdbslug"],
            wikien=mids["wikien"],
            wikijp=mids["wikijp"],
        )
        return relations


__all__ = ["Simkl"]
