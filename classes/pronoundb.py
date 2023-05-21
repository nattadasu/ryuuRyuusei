import aiohttp
from enum import Enum
from dataclasses import dataclass

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
    pronouns: Pronouns
    """The pronoun of the user."""


pronounBulk = dict[str, Pronouns]


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

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc, tb):
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

    async def get_pronouns(self, platform: Platform, id: str) -> PronounData:
        """
        Get the pronouns of a user

        Args:
            platform (Platform): The platform of the user
            id (str): The ID of the user

        Returns:
            Pronoun: The pronouns of the user
        """
        params = {"platform": platform.value, "id": id}
        async with self.session.get(
            f"https://pronoundb.org/api/v1/lookup", params=params
        ) as r:
            data = await r.json()
            data["pronouns"] = Pronouns(data["pronouns"])
            return PronounData(**data)

    async def get_pronouns_bulk(
        self, platform: Platform, ids: list[str]
    ) -> pronounBulk:
        """
        Get the pronouns of multiple users

        Args:
            platform (Platform): The platform of the user
            ids (list[str]): The IDs of the users

        Returns:
            PronounBulk: The pronouns of the users
        """
        params = {"platform": platform.value, "ids": ",".join(ids)}
        async with self.session.get(
            f"https://pronoundb.org/api/v1/lookup-bulk", params=params
        ) as r:
            data = await r.json()
            for key, value in data.items():
                data[key] = Pronouns(value)
            return data

    def translate_shorthand(self, pronouns: Pronouns) -> str:
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
