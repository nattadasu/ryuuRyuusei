#!/usr/bin/env python3

from io import StringIO
from typing import Any

import aiohttp
import pandas as pd

from classes.cache import Caching

MAIN_SITE = r"https://animeapi.my.id/animeapi.tsv"
CACHE_PATH = "cache/"
FILE_NAME = "mal.remote.tsv"

Cache = Caching(cache_directory=CACHE_PATH, cache_expiration_time=86400)
FILE_PATH = Cache.get_cache_path(FILE_NAME)


async def mal_get_data() -> None:
    """Fetches data from MAIN_SITE and saves it to a TSV file."""
    async with aiohttp.ClientSession() as session, session.get(MAIN_SITE) as response:
        if response.status not in [200, 302, 304]:
            print(f"Error fetching data: HTTP {response.status}: {response.reason}")
            return
        data = await response.text()
    Cache.write_cache(FILE_PATH, data)


def mal_load_data() -> str:
    """
    Loads data from the TSV file and returns it as a string.

    Returns:
        str: Loaded data.
    """
    return Cache.read_cache(FILE_PATH)


async def mal_run() -> None:
    """Fetches MyAnimeList data, processes it, and saves it to a CSV file."""
    is_valid = Cache.read_cache(FILE_PATH)
    if is_valid is None:
        await mal_get_data()
    data = mal_load_data()
    df = pd.read_csv(StringIO(data), sep="\t")
    # only select title and myAnimelist columns
    df = df[["myanimelist", "title"]]
    # drop rows with null myanimelist values
    df = df.dropna(subset=["myanimelist"])
    # convert myanimelist to int
    df["myanimelist"] = df["myanimelist"].astype(int)
    # rename myanimelist to mal_id
    df.rename(columns={"myanimelist": "mal_id"}, inplace=True)
    # sort by mal_id
    df.sort_values(by="mal_id", inplace=True)
    # save to csv file with utf-8 encoding and \t as delimiter
    df.to_csv("database/mal.csv", encoding="utf-8", sep="\t", index=False)
