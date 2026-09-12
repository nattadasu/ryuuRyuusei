from dataclasses import dataclass
from enum import Enum
from typing import Literal

import pandas as pd

from modules.commons import get_random_seed
from modules.filecache import cached_file
from modules.platforms import Platform

NEKOMIMI_DB_PATH = "database/nekomimiDb.tsv"
"""Path to the nekomimiDb TSV source file"""


def _load_nekomimi_db() -> pd.DataFrame:
    """Parse the nekomimiDb TSV once (NaNs filled once, not per command)."""
    return pd.read_csv(NEKOMIMI_DB_PATH, sep="\t").fillna("")


class NekomimiGender(Enum):
    """Supported NekomimiGender Enum"""

    BOY = "boy"
    GIRL = "girl"
    UNKNOWN = NONBINARY = NB = "nb"
    BOTH = "both"


@dataclass
class NekomimiDbStruct:
    """NekomimiDb Structure"""

    id: int
    """ID of the image"""
    imageUrl: str
    """Image URL"""
    artist: str
    """Artist name"""
    artistUrl: str
    """Artist Homepage URL"""
    platform: Platform
    """Platform of the image"""
    imageSourceUrl: str
    """Image Source URL on the platform"""
    mediaSource: str | None
    """Media Source of the image"""
    girlOrBoy: NekomimiGender
    """NekomimiGender of featured character(s)"""


class NekomimiDb:
    """
    # nattadasu/nekomimiDb Official Class for Ryuuzaki Ryuusei

    This class is used to get random nekomimi images from the database.

    ## Usage

    >>> from classes.nekomimidb import NekomimiDb
    >>> # get a random nekomimi image
    >>> nm = NekomimiDb()
    >>> embed = nm.get_random_nekomimi()
    >>> await ctx.send(embed=embed)
    """

    def __init__(
        self,
        gender: NekomimiGender | Literal["boy", "girl", "nb", "both"] | None = None,
    ):
        """
        Initialize a Nekomimi object

        Args:
            gender (NekomimiGender | Literal['boy', 'girl', 'nb', 'both'] | None): gender of a character to get the image, defaults to None
        """
        if isinstance(gender, NekomimiGender):
            self.gender = gender.value
        else:
            self.gender = gender
        self.seed = get_random_seed()
        self.nmDb = cached_file(NEKOMIMI_DB_PATH, _load_nekomimi_db)

    def get_random_nekomimi(self) -> NekomimiDbStruct:
        """
        Get a random nekomimi image from the database

        Returns:
            Series: a random row from the database
        """
        if self.gender is not None:
            query = self.nmDb[self.nmDb["girlOrBoy"] == self.gender]
        else:
            query = self.nmDb
        # get a random row from the query
        row = query.sample(n=1, random_state=self.seed)
        return NekomimiDbStruct(
            id=row["id"].values[0],
            imageUrl=row["imageUrl"].values[0],
            artist=row["artist"].values[0],
            artistUrl=row["artistUrl"].values[0],
            platform=Platform(row["platform"].values[0]),
            imageSourceUrl=row["imageSourceUrl"].values[0],
            mediaSource=row["mediaSource"].values[0],
            girlOrBoy=NekomimiGender(row["girlOrBoy"].values[0]),
        )
