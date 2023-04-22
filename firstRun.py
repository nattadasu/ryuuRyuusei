#!/usr/bin/env python3
"""A script to run first-time setup for a Discord bot.

This script installs dependencies, prepares the database, fetches data from GitHub,
indexes MyAnimeList data from AnimeAPI, builds a language index, and copies .env.example to .env.

Usage: python3 firstRun.py

Example: python3 firstRun.py
"""

import os
import shlex
import subprocess

from modules.oobe.commons import (checkTermux, current_os, prepare_database,
                                  py_bin_path)
from modules.oobe.getNekomimi import nk_run
from modules.oobe.i18nBuild import convert_langs_to_json
from modules.oobe.jikan import install_jikanpy, update_jikanpy
from modules.oobe.malIndexer import mal_run


def first_run(py_bin: str = py_bin_path()):
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
    env = "MATHLAB=\"m\" " if checkTermux() else ""
    # Check if jikanpy is installed and up-to-date
    try:
        from jikanpy import AioJikan
        print("Checking for jikanpy updates...")
        os.chdir("jikanpy")
        os.system("git pull")
        if os.system("git diff --exit-code origin/master") != 0:
            update_jikanpy()
        os.chdir("..")
        del AioJikan
    except ImportError:
        install_jikanpy()
    # Install dependencies
    print("Installing and upgrading dependencies for the next step and the bot itself...")
    # os.system(f"{env}{py_bin} -m pip install -U -r requirements.txt")
    if current_os() == "Windows":
        subprocess.run([env + py_bin, "-m", "pip", "install", "-U", "-r", "requirements.txt"], shell=False)
    else:
        os.system(shlex.join([env + shlex.quote(py_bin), "-m", "pip", "install", "-U", "-r", "requirements.txt"]))
    # Prepare the database
    print("Preparing the database as database.csv in tabbed format...")
    prepare_database()
    # Fetch data from GitHub
    print("Fetching the latest github:nattadasu/nekomimiDb data...")
    nk_run()
    # Index MyAnimeList data from AnimeAPI
    print("Indexing MyAnimeList data from AnimeAPI...")
    mal_run()
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
    first_run()
