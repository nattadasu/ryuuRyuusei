#!/usr/bin/env python3

import json
import os
import time
from typing import Dict

import aiohttp
import pandas as pd

MAIN_SITE = "https://aniapi.nattadasu.my.id/myanimelist%28%29.json"


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
    with open("cache/mal.json", "w", encoding="utf8") as f:
        json.dump(data, f, ensure_ascii=False)


def mal_load_data() -> Dict:
    """
    Loads data from the JSON file and returns it as a dictionary.

    Returns:
        dict: Loaded data.
    """
    with open("cache/mal.json", "r") as f:
        data = json.load(f)
    return data


async def mal_run() -> None:
    """Fetches MyAnimeList data, processes it, and saves it to a CSV file."""
    if not os.path.exists("cache/mal.json"):
        await mal_get_data()
    else:
        # check if the file is >= 14 days old
        if os.stat("cache/mal.json").st_mtime < (time.time() - 14 * 86400):
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
