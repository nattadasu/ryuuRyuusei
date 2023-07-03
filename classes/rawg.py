"""RAWG API Wrapper"""

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Literal

from aiohttp import ClientSession

from classes.cache import Caching
from classes.excepts import ProviderHttpError, ProviderTypeError
from modules.const import RAWG_API_KEY, USER_AGENT


@dataclass
class RawgBaseData:
    """Rawg base data class"""

    # pylint: disable-next=invalid-name
    id: int
    """ID"""
    slug: str
    """Slug"""
    name: str
    """Name"""


@dataclass
class EsrbRating:
    """ESRB rating data class"""

    # pylint: disable-next=invalid-name
    id: int
    """ID"""
    slug: Literal[
        "everyone",
        "everyone-10-plus",
        "teen",
        "mature",
        "adults-only",
        "rating-pending",
    ] | None = None
    """Slug"""
    name: Literal["Everyone", "Everyone 10+", "Teen", "Mature",
                  "Adults Only", "Rating Pending"] | None = None
    """Name"""


@dataclass
class PlatformData:
    """Each platform data class"""

    # pylint: disable-next=invalid-name
    id: int | None = None
    """ID"""
    slug: str | None = None
    """Slug"""
    name: str | None = None
    """Name"""
    image: str | None = None
    """Image"""
    year_end: int | None = None
    """Year end"""
    year_start: int | None = None
    """Year start"""
    games_count: int | None = None
    """Games count"""
    image_background: str | None = None
    """Image background"""


@dataclass
class StoreData(RawgBaseData):
    """Store data class"""

    domain: str | None = None
    """Domain"""
    games_count: int | None = None
    """Games count"""
    image_background: str | None = None
    """Image background"""


@dataclass
class StudioData(RawgBaseData):
    """Studio (developer, publisher) data class"""

    games_count: int | None = None
    """Games count"""
    image_background: str | None = None
    """Image background"""


@dataclass
class GenreData(RawgBaseData):
    """Genre data class"""

    games_count: int | None = None
    """Games count"""
    image_background: str | None = None
    """Image background"""


@dataclass
class TagData(RawgBaseData):
    """Tag data class"""

    games_count: int | None = None
    """Games count"""
    image_background: str | None = None
    """Image background"""
    language: str | None = None
    """Language"""


@dataclass
class Stores:
    """Stores data class"""

    # pylint: disable-next=invalid-name
    id: int | None = None
    """ID"""
    store: StoreData | None = None
    """Store"""
    url: str | None = None
    """URL"""


@dataclass
class ParentPlatform:
    """Parent platform data class"""

    platform: PlatformData | None = None
    """Platform"""


@dataclass
class MetacriticPlatformData:
    """Metacritic platform data class"""

    platform: int | None = None
    """Platform"""
    name: str | None = None
    """Name"""
    slug: str | None = None
    """Slug"""


@dataclass
class Requirements:
    """Requirements data class"""

    minimum: str | None = None
    """Minimum"""
    recommended: str | None = None
    """Recommended"""


@dataclass
class Platforms:
    """Platforms data class"""

    platform: PlatformData | None = None
    """Platform"""
    released_at: datetime | None = None
    """Released at"""
    requirements: Requirements | None = None
    """Requirements"""


@dataclass
class MetacriticPlatforms:
    """Metacritic platforms data class"""

    metascore: int | None = None
    """Metascore"""
    url: str | None = None
    """URL"""
    platform: MetacriticPlatformData | None = None


@dataclass
class Ratings:
    """Ratings data class"""

    # pylint: disable-next=invalid-name
    id: int | None = None
    """ID"""
    title: str | None = None
    """Title"""
    count: int | None = None
    """Count"""
    percent: float | None = None
    """Percent"""


@dataclass
class AddedByStatus:
    """Added by status data class"""

    yet: int | None = None
    """Yet"""
    owned: int | None = None
    """Owned"""
    beaten: int | None = None
    """Beaten"""
    toplay: int | None = None
    """To play"""
    dropped: int | None = None
    """Dropped"""
    playing: int | None = None
    """Playing"""


@dataclass
class RawgGameData(RawgBaseData):
    """Rawg game data class"""

    name_original: str | None = None
    """Name original"""
    description: str | None = None
    """Description"""
    metacritic: int | None = None
    """Metacritic"""
    metacritic_platforms: list[MetacriticPlatforms] | None = None
    """Metacritic platforms"""
    released: datetime | None = None
    """Released"""
    tba: bool | None = None
    """To be announced (TBA) status"""
    updated: datetime | None = None
    """Updated"""
    background_image: str | None = None
    """Background image"""
    background_image_additional: str | None = None
    """Background image additional"""
    website: str | None = None
    """Website"""
    rating: float | None = None
    """Rating"""
    rating_top: int | None = None
    """Rating top"""
    ratings: list[Ratings] | None = None
    """Ratings"""
    reactions: dict[str, int | str | None] | None = None
    """Reactions"""
    added: int | None = None
    """Added"""
    added_by_status: AddedByStatus | None = None
    """Added by status"""
    playtime: timedelta | None = None
    """Playtime in hours"""
    screenshots_count: int | None = None
    """Screenshots count"""
    movies_count: int | None = None
    """Movies count"""
    creators_count: int | None = None
    """Creators count"""
    achievements_count: int | None = None
    """Achievements count"""
    parent_achievements_count: int | None = None
    """Parent achievements count"""
    reddit_url: str | None = None
    """Reddit URL"""
    reddit_name: str | None = None
    """Reddit name"""
    reddit_description: str | None = None
    """Reddit description"""
    reddit_logo: str | None = None
    """Reddit logo"""
    reddit_count: int | None = None
    """Reddit count"""
    twitch_count: int | None = None
    """Twitch count"""
    youtube_count: int | None = None
    """YouTube count"""
    reviews_text_count: int | None = None
    """Reviews text count"""
    ratings_count: int | None = None
    """Ratings count"""
    suggestions_count: int | None = None
    """Suggestions count"""
    alternative_names: list[str] | None = None
    """Alternative names"""
    metacritic_url: str | None = None
    """Metacritic URL"""
    parents_count: int | None = None
    """Parents count"""
    additions_count: int | None = None
    """Additions count"""
    game_series_count: int | None = None
    """Game series count"""
    user_game: str | None = None
    """User game"""
    reviews_count: int | None = None
    """Reviews count"""
    community_rating: int | None = None
    """Community rating"""
    saturated_color: str | None = None
    """Saturated color"""
    dominant_color: str | None = None
    """Dominant color"""
    parent_platforms: list[ParentPlatform] | None = None
    """Parent Platforms"""
    esrb_rating: EsrbRating | None = None
    """ESRB rating"""
    platforms: list[Platforms] | None = None
    """Platforms"""
    stores: list[Stores] | None = None
    """Stores"""
    developers: list[StudioData] | None = None
    """Developers"""
    genres: list[GenreData] | None = None
    """Genres"""
    tags: list[TagData] | None = None
    """Tags"""
    publishers: list[StudioData] | None = None
    """Publishers"""
    description_raw: str | None = None
    """Description raw"""
    clip: Any = None
    """Clip"""


Cache = Caching("cache/rawg", 86400)


class RawgApi:
    """RAWG API Wrapper"""

    def __init__(self, key: str = RAWG_API_KEY):
        """
        Initialize the RAWG API Wrapper

        Args:
            key (str): RAWG API key, defaults to RAWG_API_KEY
        """
        if key == "":
            raise ProviderHttpError("No API key provided", 401)
        self.base_url = "https://api.rawg.io/api"
        self.params = {"key": key}
        self.session = ClientSession(headers={"User-Agent": USER_AGENT})

    async def __aenter__(self):
        """Enter the async context manager"""
        return self

    # pylint: disable-next=invalid-name
    async def __aexit__(self, exc_type, exc, tb):  # type: ignore
        """Exit the async context manager"""
        await self.session.close()

    # pylint: disable=too-many-branches
    @staticmethod
    def _convert(data: dict[str, Any]) -> RawgGameData:
        """
        Convert RAWG API data to RawgGameData class

        Args:
            data (dict[str, Any]): RAWG API data

        Returns:
            RawgGameData: RawgGameData class
        """
        if data.get("metacritic_platforms", None):
            data["metacritic_platforms"] = [
                MetacriticPlatforms(
                    metascore=x["metascore"],
                    url=x["url"],
                    platform=MetacriticPlatformData(**x["platform"]),
                )
                for x in data["metacritic_platforms"]
            ]
        if data.get("released", None):
            rel = f'{data["released"]}T00:00:00+0000'
            data["released"] = datetime.strptime(rel, "%Y-%m-%dT%H:%M:%S%z")
        if data.get("updated", None):
            upd = f"{data['updated']}+0000"
            data["updated"] = datetime.strptime(upd, "%Y-%m-%dT%H:%M:%S%z")
        if data.get("ratings", None):
            data["ratings"] = [Ratings(**x) for x in data["ratings"]]
        if data.get("added_by_status", None):
            data["added_by_status"] = AddedByStatus(**data["added_by_status"])
        if data.get("playtime", None):
            data["playtime"] = timedelta(hours=data["playtime"])
        if data.get("parent_platforms", None):
            data["parent_platforms"] = [
                ParentPlatform(PlatformData(**x["platform"]))
                for x in data["parent_platforms"]
            ]
        if data.get("platforms", None):
            data["platforms"] = [
                Platforms(
                    platform=PlatformData(**x["platform"]),
                    released_at=datetime.strptime(
                        f'{x["released_at"]}T00:00:00+0000', "%Y-%m-%dT%H:%M:%S%z"
                    )
                    if x["released_at"]
                    else None,
                    requirements=Requirements(**x["requirements"])
                    if x["requirements"]
                    else None,
                )
                for x in data["platforms"]
            ]
        if data.get("stores", None):
            data["stores"] = [
                Stores(
                    store=StoreData(**x["store"]),
                    url=x["url"],
                    id=x["id"],
                )
                for x in data["stores"]
            ]
        if data.get("developers", None):
            data["developers"] = [StudioData(**x) for x in data["developers"]]
        if data.get("publishers", None):
            data["publishers"] = [StudioData(**x) for x in data["publishers"]]
        if data.get("genres", None):
            data["genres"] = [GenreData(**x) for x in data["genres"]]
        if data.get("tags", None):
            data["tags"] = [TagData(**x) for x in data["tags"]]
        if data.get("esrb_rating", None):
            data["esrb_rating"] = EsrbRating(**data["esrb_rating"])
        if data.get("description_raw", None):
            data["description_raw"] = data["description_raw"].replace(
                "<br>", "\n")

        return RawgGameData(**data)

    async def search(self, query: str) -> list[dict[str, Any]]:
        """
        Search game on RAWG

        Args:
            query (str): The query

        Raises:
            ProviderHttpError: If RAWG API returns an error

        Returns:
            list[dict]: Game data
        """
        # deep copy the params
        params: dict[str, Any] = deepcopy(self.params)
        params["search"] = query
        params["page_size"] = 5
        async with self.session.get(self.base_url + "/games", params=params) as resp:
            if resp.status == 200:
                rawg_resp = await resp.json()
                return rawg_resp["results"]
            raise ProviderHttpError(
                f"RAWG API returned {resp.status}. Reason: {resp.text()}",
                resp.status)

    async def get_data(self, slug: str) -> RawgGameData:
        """
        Get information of a title in RAWG

        Args:
            slug (str): The slug

        Raises:
            ProviderHttpError: If RAWG API returns an error
            ProviderTypeError: If RAWG API returns no results

        Returns:
            RawgGameData: Game data
        """
        cache_file_path = Cache.get_cache_file_path(f"{slug}.json")
        cached_data = Cache.read_cached_data(cache_file_path)
        if cached_data is not None:
            return self._convert(cached_data)
        async with self.session.get(
            f"https://api.rawg.io/api/games/{slug}", params=self.params
        ) as resp:
            if resp.status == 200:
                rawg_resp = await resp.json()
                Cache.write_data_to_cache(rawg_resp, cache_file_path)
            else:
                raise ProviderHttpError(
                    f"RAWG API returned {resp.status}. Reason: {resp.text()}",
                    resp.status,
                )
        if len(rawg_resp) == 0:
            raise ProviderTypeError("**No results found!**", dict)
        return self._convert(rawg_resp)
