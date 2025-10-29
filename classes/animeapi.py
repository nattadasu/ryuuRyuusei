from datetime import datetime as dt
from typing import Literal

from animeapi import AsyncAnimeAPI, Platform
from animeapi.models import AnimeRelation

from modules.commons import save_traceback_to_file


class _SystemUser:
    """Mock user object for system-level errors"""
    id = 0


class AnimeApi:
    """AnimeAPI API Wrapper"""

    def __init__(self):
        """Initialize the AniAPI API Wrapper"""
        self.api = AsyncAnimeAPI()

    async def __aenter__(self):
        """Create the session with aiohttp"""
        await self.api.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Close the session"""
        await self.api.__aexit__(exc_type, exc_val, exc_tb)

    async def close(self) -> None:
        """Close the session"""
        await self.api.close()

    AnimeApiPlatforms = Platform

    async def get_update_time(self) -> dt:
        """
        Get the last update time of AniAPI's database
        Returns:
            datetime: The last update time of AniAPI's database
        """
        try:
            resp = await self.api.get_updated_time()
            return resp.datetime()
        except BaseException as e:
            raise Exception(
                "Failed to get the last update time of AnimeAPI's database, reason: "
                + str(e)
            )

    async def get_relation(
        self,
        media_id: str | int,
        platform: Platform
        | Literal[
            "anisearch",
            "anidb",
            "anilist",
            "animenewsnetwork",
            "animeplanet",
            "annict",
            "kaize",
            "kitsu",
            "livechart",
            "myanimelist",
            "nautiljon",
            "notify",
            "otakotaku",
            "simkl",
            "shikimori",
            "shoboi",
            "silveryasha",
            "trakt",
        ],
    ) -> AnimeRelation:
        """
        Get a relation between anime and other platform via Natsu's AniAPI
        Args:
            media_id (str | int): Anime ID
            platform (Platform | Literal["anisearch", "anidb", "anilist", "animeplanet", "annict", "kaize", "kitsu", "livechart", "myanimelist", "notify", "otakotaku", "shikimori", "shoboi", "silveryasha", "trakt" ]): Platform to get the relation
        Returns:
            AnimeRelation: Relation between anime and other platform
        """
        if not isinstance(platform, Platform):
            platform = Platform(platform)
        try:
            return await self.api.get_anime_relations(media_id, platform)
        except BaseException as e:
            save_traceback_to_file(
                f"animeapi_{platform.value}_{media_id}",
                _SystemUser(),
                e,
                mute_error=True
            )
            return AnimeRelation(title="")


AnimeApiAnime = AnimeRelation

__all__ = ["AnimeApi", "AnimeApiAnime"]
