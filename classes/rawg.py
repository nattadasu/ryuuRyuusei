import json
import os
import time
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Literal, Any

from aiohttp import ClientSession

from classes.excepts import ProviderHttpError, ProviderTypeError
from modules.const import RAWG_API_KEY, USER_AGENT


@dataclass
class RawgBaseData:
    """Rawg base data class"""

    id: int
    """ID"""
    slug: str
    """Slug"""
    name: str
    """Name"""


@dataclass
class EsrbRating(RawgBaseData):
    """ESRB rating data class"""

    slug: Literal['everyone', 'everyone-10-plus', 'teen', 'mature', 'adults-only', 'rating-pending'] | None
    """Slug"""
    name: Literal['Everyone', 'Everyone 10+', 'Teen', 'Mature', 'Adults Only', 'Rating Pending'] | None
    """Name"""


@dataclass
class PlatformData(RawgBaseData):
    """Each platform data class"""

    id: int | None
    """ID"""
    slug: str | None
    """Slug"""
    name: str | None
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

    domain: str | None
    """Domain"""
    games_count: int | None
    """Games count"""
    image_background: str | None
    """Image background"""


@dataclass
class StudioData(RawgBaseData):
    """Studio (developer, publisher) data class"""

    games_count: int | None
    """Games count"""
    image_background: str | None
    """Image background"""


@dataclass
class GenreData(RawgBaseData):
    """Genre data class"""

    games_count: int | None
    """Games count"""
    image_background: str | None
    """Image background"""

@dataclass
class TagData(RawgBaseData):
    """Tag data class"""

    games_count: int | None
    """Games count"""
    image_background: str | None
    """Image background"""
    language: str | None
    """Language"""

@dataclass
class Stores:
    """Stores data class"""

    id: int | None
    """ID"""
    store: StoreData | None
    """Store"""
    url: str | None
    """URL"""

@dataclass
class ParentPlatform:
    """Parent platform data class"""

    platform: PlatformData | None
    """Platform"""

@dataclass
class MetacriticPlatformData:
    """Metacritic platform data class"""

    platform: int | None
    """Platform"""
    name: str | None
    """Name"""
    slug: str | None
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

    platform: PlatformData | None
    """Platform"""
    released_at: datetime | None
    """Released at"""
    requirements: Requirements | None
    """Requirements"""

@dataclass
class MetacriticPlatforms:
    """Metacritic platforms data class"""

    metascore: int | None
    """Metascore"""
    url: str | None
    """URL"""
    platform: MetacriticPlatformData | None

@dataclass
class Ratings:
    """Ratings data class"""

    id: int | None
    """ID"""
    title: str | None
    """Title"""
    count: int | None
    """Count"""
    percent: float | None
    """Percent"""

@dataclass
class AddedByStatus:
    """Added by status data class"""

    yet: int | None
    """Yet"""
    owned: int | None
    """Owned"""
    beaten: int | None
    """Beaten"""
    toplay: int | None
    """To play"""
    dropped: int | None
    """Dropped"""
    playing: int | None
    """Playing"""

@dataclass
class RawgGameData(RawgBaseData):
    """Rawg game data class"""

    name_original: str | None
    """Name original"""
    description: str | None
    """Description"""
    metacritic: int | None
    """Metacritic"""
    metacritic_platforms: list[MetacriticPlatforms] | None
    """Metacritic platforms"""
    released: datetime | None
    """Released"""
    tba: bool | None
    """To be announced (TBA) status"""
    updated: datetime | None
    """Updated"""
    background_image: str | None
    """Background image"""
    background_image_additional: str | None
    """Background image additional"""
    website: str | None
    """Website"""
    rating: float | None
    """Rating"""
    rating_top: int | None
    """Rating top"""
    ratings: list[Ratings] | None
    """Ratings"""
    reactions: dict | None
    """Reactions"""
    added: int | None
    """Added"""
    added_by_status: dict
    """Added by status"""
    playtime: timedelta | None
    """Playtime in hours"""
    screenshots_count: int | None
    """Screenshots count"""
    movies_count: int | None
    """Movies count"""
    creators_count: int | None
    """Creators count"""
    achievements_count: int | None
    """Achievements count"""
    parent_achievements_count: int | None
    """Parent achievements count"""
    reddit_url: str | None
    """Reddit URL"""
    reddit_name: str | None
    """Reddit name"""
    reddit_description: str | None
    """Reddit description"""
    reddit_logo: str | None
    """Reddit logo"""
    reddit_count: int | None
    """Reddit count"""
    twitch_count: int | None
    """Twitch count"""
    youtube_count: int | None
    """YouTube count"""
    reviews_text_count: int | None
    """Reviews text count"""
    ratings_count: int | None
    """Ratings count"""
    suggestions_count: int | None
    """Suggestions count"""
    alternative_names: list[str] | None
    """Alternative names"""
    metacritic_url: str | None
    """Metacritic URL"""
    parents_count: int | None
    """Parents count"""
    additions_count: int | None
    """Additions count"""
    game_series_count: int | None
    """Game series count"""
    user_game: str | None
    """User game"""
    reviews_count: int | None
    """Reviews count"""
    saturated_color: str | None
    """Saturated color"""
    dominant_color: str | None
    """Dominant color"""
    parent_platforms: list[ParentPlatform] | None
    """Parent Platforms"""
    esrb_rating: EsrbRating | None
    """ESRB rating"""
    platforms: list[Platforms] | None
    """Platforms"""
    stores: list[Stores] | None
    """Stores"""
    developers: list[StudioData] | None
    """Developers"""
    genres: list[GenreData] | None
    """Genres"""
    tags: list[TagData] | None
    """Tags"""
    publishers: list[StudioData] | None
    """Publishers"""
    description_raw: str | None
    """Description raw"""
    clip: Any = None
    """Clip"""


class RawgApi:
    """RAWG API Wrapper"""

    def __init__(self, key: str = RAWG_API_KEY):
        """
        Initialize the RAWG API Wrapper

        Args:
            key (str): RAWG API key, defaults to RAWG_API_KEY
        """
        if key is None:
            raise ProviderHttpError("No API key provided", 401)
        self.base_url = "https://api.rawg.io/api"
        self.params = {"key": key}
        self.session = None
        self.cache_directory = "cache/rawg"
        self.cache_expiration_time = 86400  # 1 day in seconds

    async def __aenter__(self):
        """Enter the async context manager"""
        self.session = ClientSession(headers={"User-Agent": USER_AGENT})
        return self

    async def __aexit__(self, exc_type, exc, tb):
        """Exit the async context manager"""
        await self.close()

    @staticmethod
    def _convert(data: dict) -> RawgGameData:
        """
        Convert RAWG API data to RawgGameData

        Args:
            data (dict): RAWG API data

        Returns:
            RawgGameData: Converted data
        """
        d = data
        pf = RawgGameData(
            id=d["id"],
            slug=d["slug"],
            name=d["name"],
            name_original=d["name_original"],
            description=d["description"],
            metacritic=d["metacritic"],
            metacritic_platforms=[
                MetacriticPlatforms(
                    metascore=mp["metascore"],
                    url=mp["url"],
                    platform=MetacriticPlatformData(
                        platform=mp["platform"]["platform"],
                        name=mp["platform"]["name"],
                        slug=mp["platform"]["slug"],
                    )
                ) for mp in d["metacritic_platforms"]
            ],
            released=datetime.strptime(f'{d["released"]}T00:00:00+00:00', "%Y-%m-%dT%H:%M:%S%z"),
            tba=d["tba"],
            updated=datetime.strptime(f'{d["updated"]}+00:00', "%Y-%m-%dT%H:%M:%S%z"),
            background_image=d["background_image"],
            background_image_additional=d["background_image_additional"],
            website=d["website"],
            rating=d["rating"],
            rating_top=d["rating_top"],
            ratings=[
                Ratings(
                    id=r["id"],
                    title=r["title"],
                    count=r["count"],
                    percent=r["percent"],
                ) for r in d["ratings"]
            ],
            reactions=d["reactions"],
            added=d["added"],
            added_by_status=AddedByStatus(
                yet=d["added_by_status"]["yet"],
                owned=d["added_by_status"]["owned"],
                beaten=d["added_by_status"]["beaten"],
                toplay=d["added_by_status"]["toplay"],
                dropped=d["added_by_status"]["dropped"],
                playing=d["added_by_status"]["playing"],
            ),
            playtime=timedelta(hours=float(d["playtime"])),
            screenshots_count=d["screenshots_count"],
            movies_count=d["movies_count"],
            creators_count=d["creators_count"],
            achievements_count=d["achievements_count"],
            parent_achievements_count=d["parent_achievements_count"],
            reddit_url=d["reddit_url"],
            reddit_name=d["reddit_name"],
            reddit_description=d["reddit_description"],
            reddit_logo=d["reddit_logo"],
            reddit_count=d["reddit_count"],
            twitch_count=d["twitch_count"],
            youtube_count=d["youtube_count"],
            reviews_text_count=d["reviews_text_count"],
            ratings_count=d["ratings_count"],
            suggestions_count=d["suggestions_count"],
            alternative_names=d["alternative_names"],
            metacritic_url=d["metacritic_url"],
            parents_count=d["parents_count"],
            additions_count=d["additions_count"],
            game_series_count=d["game_series_count"],
            user_game=d["user_game"],
            reviews_count=d["reviews_count"],
            saturated_color=d["saturated_color"],
            dominant_color=d["dominant_color"],
            parent_platforms=[
                ParentPlatform(
                    platform=PlatformData(
                        id=pp["platform"]["id"],
                        name=pp["platform"]["name"],
                        slug=pp["platform"]["slug"],
                    ),
                ) for pp in d["parent_platforms"]
            ],
            platforms=[
                Platforms(
                    platform=PlatformData(
                        id=p["platform"]["id"],
                        name=p["platform"]["name"],
                        slug=p["platform"]["slug"],
                        image=p["platform"]["image"],
                        year_end=p["platform"]["year_end"],
                        year_start=p["platform"]["year_start"],
                        games_count=p["platform"]["games_count"],
                        image_background=p["platform"]["image_background"],
                    ),
                    released_at=datetime.strptime(f'{p["released_at"]}T00:00:00+00:00', "%Y-%m-%dT%H:%M:%S%z"),
                    requirements=Requirements(**p["requirements"])
                ) for p in d["platforms"]
            ],
            stores=[
                Stores(
                    store=StoreData(
                        id=s["store"]["id"],
                        name=s["store"]["name"],
                        slug=s["store"]["slug"],
                        domain=s["store"]["domain"],
                        games_count=s["store"]["games_count"],
                        image_background=s["store"]["image_background"],
                    ),
                    url=s["url"],
                    id=s["id"],
                ) for s in d["stores"]
            ],
            developers=[
                StudioData(
                    id=d["id"],
                    name=d["name"],
                    slug=d["slug"],
                    games_count=d["games_count"],
                    image_background=d["image_background"],
                ) for d in d["developers"]
            ],
            genres=[
                GenreData(
                    id=g["id"],
                    name=g["name"],
                    slug=g["slug"],
                    games_count=g["games_count"],
                    image_background=g["image_background"],
                ) for g in d["genres"]
            ],
            tags=[
                TagData(
                    id=t["id"],
                    name=t["name"],
                    slug=t["slug"],
                    language=t["language"],
                    games_count=t["games_count"],
                    image_background=t["image_background"],
                ) for t in d["tags"]
            ],
            publishers=[
                StudioData(
                    id=p["id"],
                    name=p["name"],
                    slug=p["slug"],
                    games_count=p["games_count"],
                    image_background=p["image_background"],
                ) for p in d["publishers"]
            ],
            esrb_rating=EsrbRating(
                id=d["esrb_rating"]["id"],
                name=d["esrb_rating"]["name"],
                slug=d["esrb_rating"]["slug"],
            ),
            clip=None,
            description_raw=d["description_raw"],
        )

        return pf



    async def search(self, query: str) -> list[dict]:
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
        params = deepcopy(self.params)
        params["search"] = query
        params["page_size"] = 5
        async with self.session.get(self.base_url + "/games", params=params) as resp:
            if resp.status == 200:
                rawgRes = await resp.json()
                return rawgRes["results"]
            raise ProviderHttpError(
                f"RAWG API returned {resp.status}. Reason: {resp.text()}", resp.status
            )

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
        cache_file_path = self.get_cache_file_path(f"{slug}.json")
        cached_data = self.read_cached_data(cache_file_path)
        if cached_data is not None:
            return self._convert(cached_data)
        async with self.session.get(
            f"https://api.rawg.io/api/games/{slug}", params=self.params
        ) as resp:
            if resp.status == 200:
                rawgRes = await resp.json()
            else:
                raise ProviderHttpError(
                    f"RAWG API returned {resp.status}. Reason: {resp.text()}",
                    resp.status,
                )
        if len(rawgRes) == 0:
            raise ProviderTypeError("**No results found!**", dict)
        self.write_data_to_cache(rawgRes, cache_file_path)
        return self._convert(rawgRes)

    def get_cache_file_path(self, cache_file_name: str) -> str:
        """
        Get cache file path

        Args:
            cache_file_name (str): Cache file name

        Returns:
            str: Cache file path
        """
        return os.path.join(self.cache_directory, cache_file_name)

    def read_cached_data(self, cache_file_path: str) -> dict | None:
        """
        Read cached data

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
        """
        Write data to cache

        Args:
            data (any): Data to write
            cache_file_name (str): Cache file name
        """
        cache_data = {"timestamp": time.time(), "data": data}
        os.makedirs(os.path.dirname(cache_file_path), exist_ok=True)
        with open(cache_file_path, "w") as cache_file:
            json.dump(cache_data, cache_file)

    async def close(self):
        """Close the aiohttp session"""
        await self.session.close()
