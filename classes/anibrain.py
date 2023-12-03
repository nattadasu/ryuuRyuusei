"""
# AniBrain.ai Unofficial Python API Wrapper

Get a random anime/manga using AniList ID
"""

from copy import deepcopy as dcp
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from time import time
from typing import Dict, List, Literal, TypedDict

import aiohttp

from classes.excepts import ProviderHttpError
from modules.const import USER_AGENT

today = datetime.now().year


@dataclass
class AniBrainAiMedia:
    """AniBrainAI Anime dataclass"""

    id: str
    """Media ID"""
    anilistId: int
    """AniList ID"""
    myanimelistId: int | None
    """MyAnimeList ID"""
    titleRomaji: str | None
    """Romaji title"""
    titleEnglish: str | None
    """English title"""
    titleNative: str | None
    """Native title"""
    description: str | None
    """Description"""
    imgURLs: List[str] | None
    """Image URLs"""
    backgroundImgURLs: List[str] | None
    format: Literal[
        "tv",
        "tv short",
        "movie",
        "special",
        "ova",
        "ona",
        "music",
        "MANGA",
        "ONE_SHOT",
        "NOVEL",
    ] | None
    """Format"""
    genres: List[str] | None
    """Genres"""
    trailerURL: str | None
    """Trailer URL"""
    externalLinks: List[Dict[Literal["url", "site"], str]] | None
    """External links"""
    franchise: str | None
    """Parent franchise media ID"""
    franchiseSize: int | None
    """Franchise size"""
    kitsuId: int | None = None
    """Kitsu ID"""
    studios: List[str] | None = None
    """Studios"""

class AniBrainAiCountData(TypedDict):
    """AniBrainAI Count Data dict"""

    totalCount: int
    """Total count"""

class AniBrainAiCount(TypedDict):
    """AniBrainAI Count dict"""

    code: int
    """Response code"""
    data: AniBrainAiCountData

class AniBrainAI:
    """AniBrainAI Unofficial Python API Wrapper"""

    def __init__(self):
        """Initialize AniBrainAI

        Args:
            seed (int, optional): Seed for random. Defaults to None.
        """
        self.session = None
        self.base_url = "https://anibrain.ai/api/-/randomizer/recs"
        self.params = {}
        self.headers = {}

    async def __aenter__(self):
        """Create the session"""
        self.headers = {
            "User-Agent": USER_AGENT,
        }
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        """Close the session"""
        await self.close()

    async def close(self) -> None:
        """Close aiohttp session"""
        if self.session is None:
            raise RuntimeError("Session is not created")
        await self.session.close()

    class AnimeMediaType(Enum):
        """Media type enum for AniBrain AI"""

        MOVIE = "movie"
        """Movie"""
        ONA = "ona"
        """ONA"""
        OVA = "ova"
        """OVA"""
        SPECIAL = "special"
        """Special"""
        TV = "tv"
        """TV"""
        TV_SHORT = SHORT = TS = "tv short"
        """TV Short"""

    class IncExc(Enum):
        """Include or exclude enum for AniBrainAI"""

        INCLUDE = INC = 1
        """Include"""
        EXCLUDE = EXC = -1
        """Exclude"""

    class CountryOfOrigin(Enum):
        """Enum of supported country of origin for the media"""

        CHINA = CN = "China"
        """Mainland China"""
        JAPAN = JP = "Japan"
        """Japan"""
        SOUTH_KOREA = KOREA = SK = KR = "South Korea"
        """South Korea"""
        TAIWAN = TW = "Taiwan"
        """Taiwan"""

    async def _initialize_query(
        self,
        endpoint: Literal["anime", "manga"] = "anime",
        filter_country: str = "[]",
        filter_format: str = "[]",
        filter_score: int = 0,
        filter_genres: str | None = None,
        filter_release_from: int = 1917,
        filter_release_to: int = today,
        filter_franchise_count: int = 0,
        media_type: Literal["ANIME", "MANGA", "NOVEL", "ONE_SHOT"] = "ANIME",
        theme: str | None = "",
        adult: bool = False,
    ) -> AniBrainAiCount:
        """
        Initialize anime query for AniBrain AI

        Args:
            filter_country (str, optional): Country of origin. Defaults to '[]'.
            filter_format (str, optional): Media format. Defaults to '[]'.
            filter_score (int, optional): Minimum score. Defaults to 0.
            filter_genres (str, optional): Genres. Defaults to None.
            filter_release_from (int, optional): Minimum release year. Defaults to 1917.
            filter_release_to (int, optional): Maximum release year. Defaults to today.
            filter_franchise_count (int, optional): Minimum franchise count. Defaults to 0.
            media_type (Literal["ANIME", "MANGA"], optional): Media type. Defaults to "ANIME".
            theme (str, optional): Theme. Defaults to "".
            adult (bool, optional): Adult. Defaults to False.

        Returns:
            AniBrainAiCount: JSON response
        """
        if self.session is None:
            raise RuntimeError("Session is not created")
        self.params = {
            "filterCountry": filter_country,
            "filterFormat": filter_format,
            "filterScore": filter_score,
            "filterGenre": filter_genres,
            "filterRelease": f"[{filter_release_from},{filter_release_to}]",
            "filterFranchiseCount": filter_franchise_count,
            "mediaType": media_type,
            "theme": theme,
            "adult": str(adult).lower(),
        }

        async with self.session.get(
            f"{self.base_url}/count/{endpoint}", params=self.params
        ) as resp:
            if resp.status != 200:
                raise ProviderHttpError(resp.reason, resp.status)
            count = await resp.json()
            return count

    async def _do_query(
        self,
        media_type: Literal["ANIME", "MANGA", "NOVEL", "ONE_SHOT"] = "ANIME",
        filter_country: List[CountryOfOrigin] | CountryOfOrigin | Literal["[]"] = "[]",
        filter_score: int = 0,
        filter_genres: Dict[str, IncExc] | None = None,
        filter_release_from: int = 1917,
        filter_release_to: int | None = today,
        filter_format: List[AnimeMediaType] | AnimeMediaType | str | None = None,
        theme: str | None = "",
        adult: bool = False,
    ) -> list[AniBrainAiMedia]:
        """
        Do a query for AniBrain AI

        Args:
            media_type (Literal["ANIME", "MANGA", "NOVEL, "ONE_SHOT"]): Media type.
            filter_country (List[CountryOfOrigin] | CountryOfOrigin | None, optional): Country of origin. Defaults to None.
            filter_score (int, optional): Rating. Defaults to 0.
            filter_genres (Dict[str, IncExc] | None, optional): Genres. Defaults to None.
            filter_release_from (int | None, optional): Release year from. Defaults to 1917.
            filter_release_to (int | None, optional): Release year to. Defaults to today.
            filter_franchise_count (int, optional): Franchise count. Defaults to 0.
            theme (str | None, optional): Theme. Defaults to None.
            adult (bool, optional): Adult. Defaults to False.

        Returns:
            list[AniBrainAiMedia]: List of AniBrainAiMedia dataclass
        """
        if self.session is None:
            raise RuntimeError("Session is not created")
        if isinstance(filter_country, list):
            country = str([i.value for i in filter_country])
            country = country.replace("'", '"')
            country = country.replace(", ", ",")
        elif isinstance(filter_country, self.CountryOfOrigin):
            country = f'["{filter_country.value}"]'
        else:
            country = "[]"

        if media_type != "ANIME":
            media_format = f'["{media_type}"]'
        else:
            if isinstance(filter_format, list):
                media_format = str([i.value for i in filter_format])
                media_format = media_format.replace("'", '"')
                media_format = media_format.replace(", ", ",")
            elif isinstance(filter_format, self.AnimeMediaType):
                media_format = f'["{filter_format.value}"]'
            else:
                media_format = "[]"

        if isinstance(filter_genres, dict):
            genres = dcp(filter_genres)
            for i in genres:
                genres[i] = genres[i].value  # type: ignore
            genres = str(genres)
            genres = genres.replace("'", '"')
            genres = genres.replace(", ", ",")
            genres = genres.replace(": ", ":")
        else:
            genres = r"{}"

        if filter_release_to is None:
            filter_release_to = today

        # try to fetch total pages
        query = await self._initialize_query(
            endpoint="anime" if media_type == "ANIME" else "manga",
            filter_country=country,
            filter_format=media_format,
            filter_score=filter_score,
            filter_genres=genres,
            filter_release_from=filter_release_from,
            filter_release_to=filter_release_to,
            media_type="ANIME" if media_type == "ANIME" else "MANGA",
            theme=theme,
            adult=adult,
        )

        # get random page
        self.params["page"] = 1
        self.params["seed"] = int(time() * 10) * 100
        self.params["totalPossible"] = query["data"]["totalCount"]
        del self.params["filterFranchiseCount"]

        async with self.session.get(
            f"{self.base_url}/anime" if media_type == "ANIME" else f"{self.base_url}/manga",
            params=self.params
        ) as resp:
            if resp.status != 200:
                raise ProviderHttpError(resp.reason, resp.status)
            final = await resp.json()
            data_ret = [AniBrainAiMedia(**i) for i in final["data"]]
            return data_ret


    async def get_anime(
        self,
        filter_country: List[CountryOfOrigin] | CountryOfOrigin | Literal["[]"] = "[]",
        filter_score: int = 0,
        filter_genres: Dict[str, IncExc] | None = None,
        filter_release_from: int = 1917,
        filter_format: List[AnimeMediaType] | AnimeMediaType | str | None = None,
        filter_release_to: int | None = today,
        theme: str | None = "",
        adult: bool = False,
    ) -> list[AniBrainAiMedia]:
        """
        Get a random anime

        Args:
            filter_country (List[CountryOfOrigin] | CountryOfOrigin | None, optional): Country of origin. Defaults to None.
            filter_format (List[AnimeMediaType] | AnimeMediaType | None, optional): Media format. Defaults to None.
            filter_score (int, optional): Rating. Defaults to 0.
            filter_genres (Dict[str, IncExc] | None, optional): Genres. Defaults to None.
            filter_release_from (int | None, optional): Release year from. Defaults to 1917.
            filter_release_to (int | None, optional): Release year to. Defaults to today.
            media_type (Literal["ANIME"], optional): Media type. Defaults to "ANIME".
            theme (str | None, optional): Theme. Defaults to None.
            adult (bool, optional): Adult. Defaults to False.

        Returns:
            list[AniBrainAiMedia]: List of AniBrainAiMedia dataclass
        """
        return await self._do_query(
            media_type="ANIME",
            filter_country=filter_country,
            filter_score=filter_score,
            filter_genres=filter_genres,
            filter_release_from=filter_release_from,
            filter_release_to=filter_release_to,
            filter_format=filter_format,
            theme=theme,
            adult=adult,
        )

    async def get_manga(
        self,
        filter_country: List[CountryOfOrigin] | CountryOfOrigin | Literal["[]"] = "[]",
        filter_score: int = 0,
        filter_genres: Dict[str, IncExc] | None = None,
        filter_release_from: int = 1930,
        filter_release_to: int | None = today,
        theme: str | None = "",
        adult: bool = False,
    ) -> list[AniBrainAiMedia]:
        """
        Get a random manga

        Args:
            filter_country (List[CountryOfOrigin] | CountryOfOrigin | None, optional): Country of origin. Defaults to None.
            filter_format (Literal['["MANGA"]'], optional): Media format. Defaults to '["MANGA"]'.
            filter_score (int, optional): Rating. Defaults to 0.
            filter_genres (Dict[str, IncExc] | None, optional): Genres. Defaults to None.
            filter_release_from (int | None, optional): Release year from. Defaults to 1930.
            filter_release_to (int | None, optional): Release year to. Defaults to today.
            media_type (Literal["MANGA"], optional): Media type. Defaults to "MANGA".
            theme (str | None, optional): Theme. Defaults to None.
            adult (bool, optional): Adult. Defaults to False.

        Returns:
            list[AniBrainAiMedia]: List of AniBrainAiMedia dataclass
        """
        return await self._do_query(
            media_type="MANGA",
            filter_country=filter_country,
            filter_score=filter_score,
            filter_genres=filter_genres,
            filter_release_from=filter_release_from,
            filter_release_to=filter_release_to,
            theme=theme,
            adult=adult,
        )

    async def get_light_novel(
        self,
        filter_country: List[CountryOfOrigin] | CountryOfOrigin | Literal["[]"] = "[]",
        filter_score: int = 0,
        filter_genres: Dict[str, IncExc] | None = None,
        filter_release_from: int = 1979,
        filter_release_to: int | None = today,
        theme: str | None = "",
        adult: bool = False,
    ) -> list[AniBrainAiMedia]:
        """
        Get a random light novel

        Args:
            filter_country (List[CountryOfOrigin] | CountryOfOrigin | None, optional): Country of origin. Defaults to None.
            filter_score (int, optional): Rating. Defaults to 0.
            filter_genres (Dict[str, IncExc] | None, optional): Genres. Defaults to None.
            filter_release_from (int | None, optional): Release year from. Defaults to 1979.
            filter_release_to (int | None, optional): Release year to. Defaults to today.
            theme (str | None, optional): Theme. Defaults to None.
            adult (bool, optional): Adult. Defaults to False.

        Returns:
            list[AniBrainAiMedia]: List of AniBrainAiMedia dataclass
        """
        return await self._do_query(
            media_type="NOVEL",
            filter_country=filter_country,
            filter_score=filter_score,
            filter_genres=filter_genres,
            filter_release_from=filter_release_from,
            filter_release_to=filter_release_to,
            theme=theme,
            adult=adult,
        )

    async def get_one_shot(
        self,
        filter_country: List[CountryOfOrigin] | CountryOfOrigin | Literal["[]"] = "[]",
        filter_score: int = 0,
        filter_genres: Dict[str, IncExc] | None = None,
        filter_release_from: int = 1954,
        filter_release_to: int | None = today,
        theme: str | None = "",
        adult: bool = False,
    ) -> list[AniBrainAiMedia]:
        """
        Get a random one-shot

        Args:
            filter_country (List[CountryOfOrigin] | CountryOfOrigin | None, optional): Country of origin. Defaults to None.
            filter_score (int, optional): Rating. Defaults to 0.
            filter_genres (Dict[str, IncExc] | None, optional): Genres. Defaults to None.
            filter_release_from (int | None, optional): Release year from. Defaults to 1954.
            filter_release_to (int | None, optional): Release year to. Defaults to today.
            theme (str | None, optional): Theme. Defaults to None.
            adult (bool, optional): Adult. Defaults to False.

        Returns:
            list[AniBrainAiMedia]: List of AniBrainAiMedia dataclass
        """
        return await self._do_query(
            media_type="ONE_SHOT",
            filter_country=filter_country,
            filter_score=filter_score,
            filter_genres=filter_genres,
            filter_release_from=filter_release_from,
            filter_release_to=filter_release_to,
            theme=theme,
            adult=adult,
        )
