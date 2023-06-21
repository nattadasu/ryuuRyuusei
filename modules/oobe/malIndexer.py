#!/usr/bin/env python3

import json
from typing import Dict

import aiohttp
import pandas as pd

from classes.cache import Caching

MAIN_SITE = "https://aniapi.nattadasu.my.id/myanimelist%28%29.json"
CACHE_PATH = "cache/"
FILE_NAME = "mal.json"

Cache = Caching(cache_directory=CACHE_PATH, cache_expiration_time=1209600)
FILE_PATH = Cache.get_cache_path(FILE_NAME)


async def mal_get_data() -> None:
    """Fetches data from MAIN_SITE and saves it to a JSON file."""
    async with aiohttp.ClientSession() as session, session.get(MAIN_SITE) as response:
        if response.status != 200:
            print(
                f"Error fetching data: HTTP {response.status}: {response.reason}")
            return
        data = await response.text()
    # save data to json file
    data = json.loads(data)
    Cache.write_cache(FILE_PATH, data)


def mal_load_data() -> Dict:
    """
    Loads data from the JSON file and returns it as a dictionary.

    Returns:
        dict: Loaded data.
    """
    return Cache.read_cache(FILE_PATH)


async def mal_run() -> None:
    """Fetches MyAnimeList data, processes it, and saves it to a CSV file."""
    is_valid = Cache.read_cache(FILE_PATH)
    if is_valid is None:
        await mal_get_data()
    data = mal_load_data()
    df = pd.DataFrame(data)
    # only select title and myAnimeList columns
    df = df[["myanimelist", "title"]]
    # rename myAnimeList to mal_id
    df.rename(columns={"myanimelist": "mal_id"}, inplace=True)
    # sort by mal_id
    df.sort_values(by="mal_id", inplace=True)
    # save to csv file with utf-8 encoding and \t as delimiter
    df.to_csv("database/mal.csv", encoding="utf-8", sep="\t", index=False)
