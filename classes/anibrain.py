"""
# AniBrain.ai Unofficial Python API Wrapper

Get a random anime/manga using AniList ID
"""

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
    imgPrimaryColors: List[str] | None = None
    """Primary colors from images"""
    backgroundImgURLs: List[str] | None = None
    """Background image URLs"""
    format: (
        Literal[
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
        ]
        | None
    ) = None
    """Format"""
    genres: List[str] | None = None
    """Genres"""
    trailerURL: str | None = None
    """Trailer URL"""
    externalLinks: List[Dict[Literal["url", "site"], str]] | None = None
    """External links"""
    franchise: str | None = None
    """Parent franchise media ID"""
    franchiseSize: int | None = None
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
        self.base_url_count = "https://anibrain.ai/api/-/recommender/recs"
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
        filter_country: list | str = "[]",
        filter_format: list | str = "[]",
        filter_score: int = 0,
        filter_genres: dict | str = "{}",
        filter_tags: dict | str = '{"min":{},"max":{}}',
        filter_release_from: int = 1917,
        filter_release_to: int = today,
        media_type: Literal["ANIME", "MANGA", "NOVEL", "ONE_SHOT"] = "ANIME",
        adult: bool = False,
    ) -> AniBrainAiCount:
        """
        Initialize anime query for AniBrain AI

        Args:
            endpoint: API endpoint (anime or manga)
            filter_country: Country of origin as JSON array string
            filter_format: Media format as JSON array string
            filter_score: Minimum score
            filter_genres: Genres as JSON object string
            filter_tags: Tags with min/max as JSON object string
            filter_release_from: Minimum release year
            filter_release_to: Maximum release year
            media_type: Media type
            adult: Adult content flag

        Returns:
            AniBrainAiCount: JSON response with count
        """
        if self.session is None:
            raise RuntimeError("Session is not created")
        self.params = {
            "filterCountry": filter_country,
            "filterFormat": filter_format,
            "filterGenre": filter_genres,
            "filterTag": filter_tags,
            "filterRelease": f"[{filter_release_from},{filter_release_to}]",
            "filterScore": str(filter_score),
            "mediaType": media_type,
            "adult": str(adult).lower(),
        }

        async with self.session.get(
            f"{self.base_url_count}/count/{endpoint}", params=self.params
        ) as resp:
            if resp.status != 200:
                raise ProviderHttpError(resp.reason, resp.status)
            count = await resp.json()
            return count

    def _format_country_list(
        self, filter_country: List[CountryOfOrigin] | CountryOfOrigin | Literal["[]"]
    ) -> list[str]:
        """Convert country filter to list of country strings"""
        if isinstance(filter_country, list):
            return [i.value for i in filter_country]
        elif isinstance(filter_country, self.CountryOfOrigin):
            return [filter_country.value]
        return []

    def _format_media_format(
        self,
        media_type: Literal["ANIME", "MANGA", "NOVEL", "ONE_SHOT"],
        filter_format: List[AnimeMediaType] | AnimeMediaType | str | None = None,
    ) -> list[str]:
        """Convert format filter to list of format strings"""
        if media_type == "ANIME":
            if isinstance(filter_format, list):
                return [i.value for i in filter_format]
            elif isinstance(filter_format, self.AnimeMediaType):
                return [filter_format.value]
            elif isinstance(filter_format, str) and filter_format == "[]":
                return []
            return []
        # For manga/novel/one-shot, format must be the media type itself
        return [media_type]

    def _format_genres(self, filter_genres: Dict[str, IncExc] | None) -> dict:
        """Convert genre filter to dict with integer values"""
        if isinstance(filter_genres, dict):
            return {k: v.value for k, v in filter_genres.items()}
        return {}

    def _build_params(
        self,
        country_str: str,
        format_str: str,
        genres_str: str,
        tags_str: str,
        filter_release_from: int,
        filter_release_to: int,
        filter_score: int,
        media_type: Literal["ANIME", "MANGA"],
        adult: bool,
        total_possible: int,
    ) -> dict[str, str]:
        """Build query parameters dictionary"""
        return {
            "filterCountry": country_str,
            "filterFormat": format_str,
            "filterGenre": genres_str,
            "filterTag": tags_str,
            "filterRelease": f"[{filter_release_from},{filter_release_to}]",
            "filterScore": str(filter_score),
            "mediaType": media_type,
            "adult": str(adult).lower(),
            "page": "1",
            "seed": str(int(time() * 1000)),
            "totalPossible": str(total_possible),
        }

    def _get_endpoint_type(
        self, media_type: Literal["ANIME", "MANGA", "NOVEL", "ONE_SHOT"]
    ) -> tuple[str, str]:
        """Get API endpoint and media type string for the given media type"""
        if media_type == "ANIME":
            return ("anime", "ANIME")
        return ("manga", "MANGA")

    async def _do_query(
        self,
        media_type: Literal["ANIME", "MANGA", "NOVEL", "ONE_SHOT"] = "ANIME",
        filter_country: List[CountryOfOrigin] | CountryOfOrigin | Literal["[]"] = "[]",
        filter_score: int = 0,
        filter_genres: Dict[str, IncExc] | None = None,
        filter_release_from: int = 1917,
        filter_release_to: int | None = today,
        filter_format: List[AnimeMediaType] | AnimeMediaType | str | None = None,
        adult: bool = False,
    ) -> list[AniBrainAiMedia]:
        """
        Do a query for AniBrain AI

        Args:
            media_type: Media type (ANIME, MANGA, NOVEL, ONE_SHOT)
            filter_country: Country of origin filter
            filter_score: Minimum score (NOTE: AniBrain randomizer only supports 0)
            filter_genres: Genre filters with include/exclude
            filter_release_from: Release year from
            filter_release_to: Release year to
            filter_format: Media format filter (only for anime)
            adult: Include adult content

        Returns:
            list[AniBrainAiMedia]: List of media results
        """
        if self.session is None:
            raise RuntimeError("Session is not created")

        # AniBrain randomizer endpoint only supports score=0
        filter_score = 0

        # Format filters using helper methods
        country = self._format_country_list(filter_country)
        media_format = self._format_media_format(media_type, filter_format)
        genres = self._format_genres(filter_genres)

        if filter_release_to is None:
            filter_release_to = today

        # Convert to JSON strings for API (no spaces after delimiters)
        import json

        country_str = json.dumps(country, separators=(",", ":"))
        format_str = json.dumps(media_format, separators=(",", ":"))
        genres_str = json.dumps(genres, separators=(",", ":"))
        tags_str = json.dumps({"min": {}, "max": {}}, separators=(",", ":"))

        # Get endpoint type
        endpoint, api_media_type = self._get_endpoint_type(media_type)

        # Get total count first
        try:
            query = await self._initialize_query(
                endpoint=endpoint,
                filter_country=country_str,
                filter_format=format_str,
                filter_score=filter_score,
                filter_genres=genres_str,
                filter_tags=tags_str,
                filter_release_from=filter_release_from,
                filter_release_to=filter_release_to,
                media_type=api_media_type,
                adult=adult,
            )
            total_possible = query["data"]["totalCount"]
        except (ProviderHttpError, KeyError):
            # Fallback to reasonable default if count fails
            total_possible = 50000

        # Build query parameters using helper method
        self.params = self._build_params(
            country_str,
            format_str,
            genres_str,
            tags_str,
            filter_release_from,
            filter_release_to,
            filter_score,
            api_media_type,
            adult,
            total_possible,
        )

        async with self.session.get(
            f"{self.base_url}/{endpoint}", params=self.params
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
        adult: bool = False,
    ) -> list[AniBrainAiMedia]:
        """
        Get a random anime

        Args:
            filter_country: Country of origin filter
            filter_score: Minimum score (0-100)
            filter_genres: Genre filters with include/exclude
            filter_release_from: Release year from
            filter_format: Media format filter
            filter_release_to: Release year to
            adult: Include adult content

        Returns:
            list[AniBrainAiMedia]: List of anime results
        """
        return await self._do_query(
            media_type="ANIME",
            filter_country=filter_country,
            filter_score=filter_score,
            filter_genres=filter_genres,
            filter_release_from=filter_release_from,
            filter_release_to=filter_release_to,
            filter_format=filter_format,
            adult=adult,
        )

    async def get_manga(
        self,
        filter_country: List[CountryOfOrigin] | CountryOfOrigin | Literal["[]"] = "[]",
        filter_score: int = 0,
        filter_genres: Dict[str, IncExc] | None = None,
        filter_release_from: int = 1930,
        filter_release_to: int | None = today,
        adult: bool = False,
    ) -> list[AniBrainAiMedia]:
        """
        Get a random manga

        Args:
            filter_country: Country of origin filter
            filter_score: Minimum score (0-100)
            filter_genres: Genre filters with include/exclude
            filter_release_from: Release year from
            filter_release_to: Release year to
            adult: Include adult content

        Returns:
            list[AniBrainAiMedia]: List of manga results
        """
        return await self._do_query(
            media_type="MANGA",
            filter_country=filter_country,
            filter_score=filter_score,
            filter_genres=filter_genres,
            filter_release_from=filter_release_from,
            filter_release_to=filter_release_to,
            adult=adult,
        )

    async def get_light_novel(
        self,
        filter_country: List[CountryOfOrigin] | CountryOfOrigin | Literal["[]"] = "[]",
        filter_score: int = 0,
        filter_genres: Dict[str, IncExc] | None = None,
        filter_release_from: int = 1979,
        filter_release_to: int | None = today,
        adult: bool = False,
    ) -> list[AniBrainAiMedia]:
        """
        Get a random light novel

        Args:
            filter_country: Country of origin filter
            filter_score: Minimum score (0-100)
            filter_genres: Genre filters with include/exclude
            filter_release_from: Release year from
            filter_release_to: Release year to
            adult: Include adult content

        Returns:
            list[AniBrainAiMedia]: List of light novel results
        """
        return await self._do_query(
            media_type="NOVEL",
            filter_country=filter_country,
            filter_score=filter_score,
            filter_genres=filter_genres,
            filter_release_from=filter_release_from,
            filter_release_to=filter_release_to,
            adult=adult,
        )

    async def get_one_shot(
        self,
        filter_country: List[CountryOfOrigin] | CountryOfOrigin | Literal["[]"] = "[]",
        filter_score: int = 0,
        filter_genres: Dict[str, IncExc] | None = None,
        filter_release_from: int = 1954,
        filter_release_to: int | None = today,
        adult: bool = False,
    ) -> list[AniBrainAiMedia]:
        """
        Get a random one-shot

        Args:
            filter_country: Country of origin filter
            filter_score: Minimum score (0-100)
            filter_genres: Genre filters with include/exclude
            filter_release_from: Release year from
            filter_release_to: Release year to
            adult: Include adult content

        Returns:
            list[AniBrainAiMedia]: List of one-shot results
        """
        return await self._do_query(
            media_type="ONE_SHOT",
            filter_country=filter_country,
            filter_score=filter_score,
            filter_genres=filter_genres,
            filter_release_from=filter_release_from,
            filter_release_to=filter_release_to,
            adult=adult,
        )
