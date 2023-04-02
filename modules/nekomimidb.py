from modules.commons import *


async def getNekomimi(gender: str = None) -> dict:
    """Get a random nekomimi image from the database"""
    seed = getRandom()
    nmDb = pd.read_csv("database/nekomimiDb.tsv", sep="\t")
    nmDb = nmDb.fillna('')
    if gender is not None:
        query = nmDb[nmDb['girlOrBoy'] == f'{gender}']
    else:
        query = nmDb
    # get a random row from the query
    row = query.sample(n=1, random_state=seed)
    return row
