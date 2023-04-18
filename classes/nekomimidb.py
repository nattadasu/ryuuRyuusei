from enum import Enum

import pandas as pd
from interactions import Embed, EmbedAttachment, EmbedAuthor, EmbedField

from modules.commons import getRandom
from modules.platforms import getPlatformColor


class NekomimiDb:
    """# nattadasu/nekomimiDb Official Class for Ryuuzaki Ryuusei

    This class is used to get random nekomimi images from the database.

    ## Usage

    ```py
    from classes.nekomimidb import NekomimiDb

    # get a random nekomimi image
    nm = NekomimiDb()
    embed = nm.get_random_nekomimi()
    await ctx.send(embed=embed)
    ```"""
    class Gender(Enum):
        BOY = "boy"
        GIRL = "girl"
        NB = "nb"
        BOTH = "both"

    def __init__(self, gender: Gender = None):
        """Initialize a Nekomimi object"""
        self.gender = gender
        self.seed = getRandom()
        self.nmDb = pd.read_csv("database/nekomimiDb.tsv", sep="\t").fillna('')

    def get_random_nekomimi(self) -> pd.Series:
        """Get a random nekomimi image from the database"""
        if self.gender is not None:
            query = self.nmDb[self.nmDb['girlOrBoy'] == self.gender.value]
        else:
            query = self.nmDb
        # get a random row from the query
        row = query.sample(n=1, random_state=self.seed)
        return row

