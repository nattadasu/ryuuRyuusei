"""Mangadex API Handler for extensions/mediaautosend.py"""
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal

import aiohttp
from dacite import from_dict, Config

from classes.cache import Caching
from classes.excepts import ProviderHttpError
from modules.const import USER_AGENT

cache_ = Caching(cache_directory="cache/mangadex", cache_expiration_time=86400)

# pylint: disable=invalid-name
@dataclass
class DatabaseLinks:
    """Links to external databases"""

    al: str | None = None
    """AniList"""
    ap: str | None = None
    """Anime-Planet"""
    amz: str | None = None
    """Amazon"""
    bw: str | None = None
    """Book☆Walker"""
    cdj: str | None = None
    """CDJapan"""
    ebj: str | None = None
    """eBookJapan"""
    mu: str | None = None
    """MangaUpdates"""
    nu: str | None = None
    """NovelUpdates"""
    kt: str | None = None
    """Kitsu"""
    mal: str | None = None
    """MyAnimeList"""
    raw: str | None = None
    """Raw"""


@dataclass
class TagAttributes:
    """Tag Attributes Dataclass"""
    name: dict[
        Literal["en", "ja", "ja-ro"] | str,
        str
    ]
    """Tag name"""
    description: dict[
        Literal["en", "ja"] | str,
        str
    ] | None
    """Tag description"""
    group: Literal[
        "genre",
        "theme",
        "format",
        "content",
        "demographic",
        "none"
    ] | None
    """Tag group"""
    version: int
    """Tag version"""


@dataclass
class Tag:
    """Tag Dataclass"""
    id: str
    """Tag ID"""
    type: Literal["tag"]
    """Tag type"""
    attributes: TagAttributes
    """Tag attributes"""
    relationships: list[Any] | None
    """Tag relationships"""


@dataclass
class MangaAttributes:
    """Manga Attributes Dataclass"""

    title: dict[
        Literal["en", "ja", "ja-ro"] | str,
        str
    ]
    """Manga main title"""
    altTitles: list[dict[
        Literal["en", "ja", "ja-ro"] | str,
        str
    ]] | None
    """Manga alternative titles"""
    description: dict[
        Literal["en", "ja"] | str,
        str
    ] | None
    """Manga description"""
    isLocked: bool
    """Whether the manga is locked or not"""
    links: DatabaseLinks | None
    """Links to external databases"""
    originalLanguage: str
    """Manga original language"""
    lastVolume: str | None
    """Manga last volume"""
    lastChapter: str | None
    """Manga last chapter"""
    publicationDemographic: Literal[
        "shounen",
        "shoujo",
        "josei",
        "seinen",
        "none"
    ] | None
    """Manga publication demographic"""
    status: Literal[
        "ongoing",
        "completed",
        "hiatus",
        "cancelled",
        "none"
    ] | None
    """Manga status"""
    year: int | None
    """Manga year"""
    contentRating: Literal[
        "safe",
        "suggestive",
        "erotica",
        "none"
    ] | None
    """Manga content rating"""
    chapterNumbersResetOnNewVolume: bool
    """Whether the chapter numbers reset on new volume or not"""
    latestUploadedChapter: str | None
    """Manga latest uploaded chapter"""
    tags: list[Tag] | None
    """Manga tags"""
    state: str | None
    """Manga state"""
    version: int
    """Manga version"""
    createdAt: datetime | str | None
    """Manga creation date"""
    updatedAt: datetime | str | None
    """Manga last update date"""
    availableTranslatedLanguage: list[str] | None
    """Manga available translated languages"""


@dataclass
class Manga:
    """Manga Dataclass"""

    id: str
    """Manga ID"""
    type: Literal["manga"]
    """Manga type"""
    attributes: MangaAttributes
    """Manga attributes"""
    relationships: list[Any] | None
    """Manga relationships"""


@dataclass
class DataResponse:
    """Data Response Dataclass"""

    result: Literal["ok", "error"]
    """Result"""
    response: Manga | None
    """Response"""
    errors: list[dict[str, str|int]] | None
    """Errors"""


class Mangadex:
    """Mangadex API Handler"""

    def __init__(self) -> None:
        self.session = None
        self.headers = {
            "User-Agent": USER_AGENT
        }

    async def __aenter__(self) -> "Mangadex":
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.session.close()

    async def _request(self, url: str) -> dict[str, Any]:
        """Make a request to the Mangadex API"""
        if not self.session:
            raise RuntimeError("Mangadex not initialized with async context manager")
        async with self.session.get(url) as response:
            if response.status != 200:
                raise ProviderHttpError(
                    await response.text(),
                    response.status
                )
            return await response.json()

    async def get_manga(self, manga_id: str) -> Manga:
        """Get a manga by its ID"""
        cache_file_path = cache_.get_cache_path(f"manga/{manga_id}.json")
        cached_data = cache_.read_cache(cache_file_path)
        dacite_config = Config(
            type_hooks={
                datetime: lambda value: datetime.fromisoformat(value)
            }
        )
        if cached_data:
            return from_dict(Manga, cached_data, config=dacite_config)
        data = await self._request(f"https://api.mangadex.org/manga/{manga_id}")
        cache_.write_cache(cache_file_path, data["data"])
        return from_dict(Manga, data["data"], config=dacite_config)
