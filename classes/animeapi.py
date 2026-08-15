from datetime import datetime as dt
from typing import Literal

from animeapi import AsyncAnimeAPI, Platform
from animeapi.models import AnimeRelation, TmdbMediaType, TraktMediaType

from classes.excepts import ProviderHttpError
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
    AnimeApiTraktMediaType = TraktMediaType
    AnimeApiTmdbMediaType = TmdbMediaType

    async def get_update_time(self) -> dt:
        """
        Get the last update time of AniAPI's database
        Returns:
            datetime: The last update time of AniAPI's database
        """
        try:
            resp = await self.api.get_updated_time()
            return resp.datetime()
        except Exception as e:
            raise ProviderHttpError(
                "Failed to get the last update time of AnimeAPI's database, reason: "
                + str(e)
            ) from e

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
            "themoviedb",
            "thetvdb",
            "trakt",
        ],
        media_type: TraktMediaType | TmdbMediaType | str | None = None,
        title_season: int | None = None,
    ) -> AnimeRelation:
        """
        Get relation between anime and other platform
        Args:
            media_id (str | int): ID of the media
            platform (Platform): Platform to get relation from
            media_type (TraktMediaType | TmdbMediaType | str, optional): Type of the media. Defaults to None.
            title_season (int, optional): Season number of the media. Defaults to None.

        Returns:
            AnimeRelation: Relation between anime and other platform
        """
        if not isinstance(platform, Platform):
            platform = Platform(platform)
        if isinstance(media_type, str):
            try:
                media_type = (
                    TmdbMediaType(media_type)
                    if platform == Platform.THEMOVIEDB
                    else TraktMediaType(media_type)
                    if platform == Platform.TRAKT
                    else media_type
                )
            except ValueError:
                pass

        try:
            return await self.api.get_anime_relations(
                media_id, platform, media_type, title_season
            )
        except Exception as e:  # noqa: BLE001
            save_traceback_to_file(
                f"animeapi_{platform.value}_{media_id}",
                _SystemUser(),
                e,
                mute_error=True,
            )
            return AnimeRelation(title="")


AnimeApiAnime = AnimeRelation

__all__ = ["AnimeApi", "AnimeApiAnime"]
