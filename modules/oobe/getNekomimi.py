#!/usr/bin/env python3

import os
from time import time

import aiohttp

MAIN_SITE = "https://raw.githubusercontent.com/nattadasu/nekomimiDb/main/index.tsv"


async def nk_get_data() -> None:
    """
    Fetches the data from the nekomimiDb main site and writes it to file.

    Raises:
        aiohttp.ClientError: If there is an issue with the GET request.

    Returns:
        None
    """
    try:
        async with aiohttp.ClientSession() as session, session.get(
            MAIN_SITE
        ) as response:
            if response.status != 200:
                print(
                    f"Error fetching data: HTTP {response.status}: {response.reason}")
                return
            data = await response.text()
    except aiohttp.ClientError as e:
        print(f"Error fetching data: {e}")
        return
    # save data to file
    with open("database/nekomimiDb.tsv", "w") as f:
        f.write(data)


async def nk_run() -> None:
    """
    Check if nekomimiDb.tsv file exists. If it does, check if it's >= 14 days old.
    If it is, get the latest version of the file and overwrite the old one.
    If it doesn't exist, download the latest version of the file.

    Returns:
        None
    """
    if not os.path.exists("database/nekomimiDb.tsv"):
        await nk_get_data()
    else:
        # check if the file is >= 14 days old
        if os.stat("database/nekomimiDb.tsv").st_mtime < (time() - 14 * 86400):
            await nk_get_data()
        else:
            print("nekomimiDb.tsv is up to date")
