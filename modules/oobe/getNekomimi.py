#!/usr/bin/env python3

import os
from time import time

import requests as r

MAIN_SITE = "https://raw.githubusercontent.com/nattadasu/nekomimiDb/main/index.tsv"


def nk_get_data() -> None:
    """Fetches the data from the nekomimiDb main site and writes it to file.

    Raises:
        requests.exceptions.RequestException: If there is an issue with the GET request.

    Returns:
        None
    """
    try:
        response = r.get(MAIN_SITE)
        response.raise_for_status()
    except r.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return
    data = response.text
    # save data to file
    with open("database/nekomimiDb.tsv", "w") as f:
        f.write(data)


def nk_run() -> None:
    """
    Check if nekomimiDb.tsv file exists. If it does, check if it's >= 14 days old.
    If it is, get the latest version of the file and overwrite the old one.
    If it doesn't exist, download the latest version of the file.

    Returns:
        None
    """
    if not os.path.exists("database/nekomimiDb.tsv"):
        nk_get_data()
    else:
        # check if the file is >= 14 days old
        if os.stat("database/nekomimiDb.tsv").st_mtime < (time() - 14 * 86400):
            nk_get_data()
        else:
            print("nekomimiDb.tsv is up to date")
