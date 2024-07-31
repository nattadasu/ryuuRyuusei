from dataclasses import dataclass
from enum import Enum
from typing import Literal, TypedDict

import aiohttp

from classes.cache import Caching
from modules.const import USER_AGENT

Cache = Caching(cache_directory="cache/pronoundb", cache_expiration_time=604800)


en_locale = Literal["he", "it", "she", "they", "any", "ask", "avoid", "other"]

en_define = {
    "he": "he/him",
    "it": "it/its",
    "she": "she/her",
    "they": "they/them",
    "any": "any pronouns",
    "ask": "ask me my pronouns",
    "avoid": "avoid pronouns, use my name",
    "other": "other pronouns",
}


class UserSets(TypedDict):
    """The user sets of the user."""

    en: list[en_locale]
    """The English locale of the user's pronoun."""


class UserId(TypedDict):
    """The user ID of the user."""

    sets: UserSets


@dataclass
class Pronouns:
    """The pronouns of the user."""

    en: list[en_locale]
    """The English locale of the user's pronoun."""

    def __str__(self) -> str:
        return (
            ", ".join([en_define[pronoun] for pronoun in self.en])
            if self.en
            else "Not set"
        )

    def __repr__(self) -> str:
        return f"Pronouns(en={self.en})"


@dataclass
class PronounData:
    """The pronoun data of the user."""

    pronouns: Pronouns
    """The pronouns of the user."""

    def __str__(self) -> str:
        return str(self.pronouns)

    def __repr__(self) -> str:
        return f"PronounData(pronouns={self.pronouns})"


class PronounDBV2:
    """PronounDB API wrapper"""

    def __init__(self):
        """
        Initialize the wrapper

        Args:
            session (aiohttp.ClientSession): The aiohttp session to use
        """
        self.session = None
        self.headers = {"User-Agent": USER_AGENT}
        self.base_url = "https://pronoundb.org/api/v2"

    async def __aenter__(self):
        """Enter the async context manager"""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        """Exit the async context manager"""
        await self.close()

    async def close(self):
        """Close the aiohttp session"""
        await self.session.close() if self.session else None

    class Platform(Enum):
        """The platform of the user."""

        DISCORD = "discord"
        """Discord"""
        GITHUB = "github"
        """GitHub"""
        MINECRAFT = "minecraft"
        """Minecraft"""
        TWITCH = "twitch"
        """Twitch"""
        TWITTER = "twitter"
        """Twitter"""

    async def lookup(
        self, platform: Platform, ids: list[str] | str
    ) -> dict[str, UserId]:
        """
        Looks up the data saved in PronounDB for one or more (up to 50) account
        for a given platform.

        The response is a map of IDs to the corresponding data. If an ID is not
        in our database, it will not be present in the response.

        Args:
            platform (Platform): The platform of the user
            ids (list[str] | str): The ID of the user

        Returns:
            Pronoun: The pronouns of the user
        """
        if not self.session:
            async with self:
                return await self.lookup(platform, ids)
        if isinstance(ids, list):
            if len(ids) > 50:
                raise ValueError("You can only lookup up to 50 IDs at a time.")
            ids = ",".join(ids)
        async with self.session.get(
            f"{self.base_url}/lookup", params={"platform": platform.value, "ids": ids}
        ) as r:
            return await r.json()

    async def get_pronouns(self, platform: Platform, user_id: str) -> PronounData:
        """
        Get the pronouns of a user

        Args:
            platform (Platform): The platform of the user
            user_id (str): The ID of the user

        Returns:
            Pronoun: The pronouns of the user
        """
        cache_file_path = Cache.get_cache_file_path(f"{platform.value}/{user_id}.json")
        cached_file = Cache.read_cached_data(cache_file_path)
        if cached_file:
            return PronounData(Pronouns(en=cached_file["sets"]["en"]))
        data = await self.lookup(platform, user_id)
        if not data:
            return PronounData(Pronouns(en=[]))
        user_data = data[user_id]
        Cache.write_cache(cache_file_path, user_data)
        return PronounData(Pronouns(en=user_data["sets"]["en"]))
