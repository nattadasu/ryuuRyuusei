import json
import os
import time
from dataclasses import dataclass
from enum import Enum

import aiohttp

from modules.const import USER_AGENT


class Pronouns(Enum):
    """The pronouns enum of the user."""

    HE_HIM = HEHIM = "hh"
    """He/Him"""
    HE_IT = HEIT = "hi"
    """He/It"""
    HE_SHE = HESHE = "hs"
    """He/She"""
    HE_THEY = HETHEY = "ht"
    """He/They"""
    IT_HE = ITHE = "ih"
    """It/He"""
    IT_ITS = ITITS = "ii"
    """It/Its"""
    IT_SHE = ITSHE = "is"
    """It/She"""
    IT_THEY = ITTHEY = "it"
    """It/They"""
    SHE_HE = SHEHE = "shh"
    """She/He"""
    SHE_HER = SHEHER = "sh"
    """She/Her"""
    SHE_IT = SHEIT = "si"
    """She/It"""
    SHE_THEY = SHETHEY = "st"
    """She/They"""
    THEY_HE = THEYHE = "th"
    """They/He"""
    THEY_IT = THEYIT = "ti"
    """They/It"""
    THEY_SHE = THEYSHE = "ts"
    """They/She"""
    THEY_THEM = THEYTHEM = "tt"
    """They/Them"""
    ANY = "any"
    """Any pronouns"""
    OTHER = "other"
    """Other pronouns"""
    ASK = "ask"
    """Ask user their pronouns"""
    AVOID = "avoid"
    """Avoid using pronouns, use their name instead"""
    UNSPECIFIED = "unspecified"
    """Unspecified pronouns"""


@dataclass
class PronounData:
    """PronounDB Pronoun Dataclass, for single user"""

    pronouns: Pronouns
    """The pronoun of the user."""


pronounBulk = dict[str, Pronouns]
"""PronounDB Pronoun Bulk Dataclass, for multiple users"""


class PronounDB:
    """PronounDB API wrapper"""

    def __init__(self):
        """
        Initialize the wrapper

        Args:
            session (aiohttp.ClientSession): The aiohttp session to use
        """
        self.session = None
        self.headers = {"User-Agent": USER_AGENT}
        self.cache_directory = "cache/pronoundb"
        self.cache_expiration_time = 604800

    async def __aenter__(self):
        """Enter the async context manager"""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        """Exit the async context manager"""
        await self.close()

    async def close(self):
        """Close the aiohttp session"""
        await self.session.close()

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

    async def get_pronouns(self, platform: Platform, user_id: str) -> PronounData:
        """
        Get the pronouns of a user

        Args:
            platform (Platform): The platform of the user
            user_id (str): The ID of the user

        Returns:
            Pronoun: The pronouns of the user
        """
        params = {"platform": platform.value, "id": user_id}
        cache_file_path = self.get_cache_file_path(
            f"{platform.value}/{user_id}.json")
        cached_file = self.read_cached_data(cache_file_path)
        if cached_file:
            cached_file["pronouns"] = Pronouns(cached_file["pronouns"])
            return PronounData(**cached_file)
        async with self.session.get(
            "https://pronoundb.org/api/v1/lookup", params=params
        ) as r:
            data = await r.json()
            self.write_data_to_cache(data, cache_file_path)
            data["pronouns"] = Pronouns(data["pronouns"])
            return PronounData(**data)

    async def get_pronouns_bulk(
        self, platform: Platform, user_ids: list[str]
    ) -> pronounBulk:
        """
        Get the pronouns of multiple users

        Args:
            platform (Platform): The platform of the user
            user_ids (list[str]): The IDs of the users

        Returns:
            PronounBulk: The pronouns of the users
        """
        params = {"platform": platform.value, "ids": ",".join(user_ids)}
        async with self.session.get(
            "https://pronoundb.org/api/v1/lookup-bulk", params=params
        ) as r:
            data = await r.json()
            for key, value in data.items():
                data[key] = Pronouns(value)
            return data

    @staticmethod
    def translate_shorthand(pronouns: Pronouns) -> str:
        """
        Translate the pronouns into shorthand

        Args:
            pronouns (Pronouns): The pronouns to translate

        Returns:
            str: The shorthand of the pronouns
        """
        pron: dict[Pronouns, str] = {
            Pronouns.HE_HIM: "he/him",
            Pronouns.HE_IT: "he/it",
            Pronouns.HE_SHE: "he/she",
            Pronouns.HE_THEY: "he/they",
            Pronouns.IT_HE: "it/he",
            Pronouns.IT_ITS: "it/its",
            Pronouns.IT_SHE: "it/she",
            Pronouns.IT_THEY: "it/they",
            Pronouns.SHE_HE: "she/he",
            Pronouns.SHE_HER: "she/her",
            Pronouns.SHE_IT: "she/it",
            Pronouns.SHE_THEY: "she/they",
            Pronouns.THEY_HE: "they/he",
            Pronouns.THEY_IT: "they/it",
            Pronouns.THEY_SHE: "they/she",
            Pronouns.THEY_THEM: "they/them",
            Pronouns.ANY: "any",
            Pronouns.OTHER: "other",
            Pronouns.ASK: "ask",
            Pronouns.AVOID: "avoid",
            Pronouns.UNSPECIFIED: "unspecified",
        }
        return pron[pronouns]

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
