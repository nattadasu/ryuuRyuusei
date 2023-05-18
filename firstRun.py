"""A script to run first-time setup for a Discord bot.

This script installs dependencies, prepares the database, fetches data from GitHub,
indexes MyAnimeList data from AnimeAPI, builds a language index, and copies .env.example to .env.

Usage: python3 firstRun.py

Example: python3 firstRun.py
"""

import os
import shlex
import subprocess
import asyncio

from modules.oobe.commons import check_termux, current_os, prepare_database, py_bin_path
from modules.oobe.getNekomimi import nk_run
from modules.oobe.i18nBuild import convert_langs_to_json
from modules.oobe.malIndexer import mal_run


async def first_run(py_bin: str = py_bin_path()):
    """Runs the first run script.

    Args:
        py_bin (str, optional): Path to the Python binary. Defaults to py_bin_path().

    Returns:
        None

    Raises:
        Exception: If the script is not run from the root directory.
    """
    # Check if the script is run from the root directory
    if not os.path.exists("requirements.txt"):
        raise Exception("Please run the script from the root directory.")
    # Check if Termux is used
    env = 'MATHLAB="m" ' if check_termux() else ""
    # Install dependencies
    print(
        "Installing and upgrading dependencies for the next step and the bot itself..."
    )
    if current_os() == "Windows":
        subprocess.run(
            [env + "pip", "install", "-U", "-r", "requirements.txt"],
            shell=False,
            check=True,
        )
    else:
        os.system(
            shlex.join(
                [
                    env + shlex.quote(py_bin),
                    "-m",
                    "pip",
                    "install",
                    "-U",
                    "-r",
                    "requirements.txt",
                ]
            )
        )
    # Prepare the database
    print("Preparing the database as database.csv in tabbed format...")
    prepare_database()
    # Fetch data from GitHub
    print("Fetching the latest github:nattadasu/nekomimiDb data...")
    await nk_run()
    # Index MyAnimeList data from AnimeAPI
    print("Indexing MyAnimeList data from AnimeAPI...")
    await mal_run()
    # Check if .env exists, if not, copy .env.example
    if not os.path.exists(".env"):
        print("Copying .env.example to .env...")
        if current_os() == "Windows":
            os.system("copy .env.example .env")
        else:
            os.system("cp .env.example .env")
    else:
        print(".env already exists, skipping...")
    # Build language index
    print("Building the language index...")
    convert_langs_to_json()
    print("Initialization finished. You should be able to run the bot safely now.")


if __name__ == "__main__":
    asyncio.run(first_run())
