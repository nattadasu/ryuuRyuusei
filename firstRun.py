"""
A script to run first-time setup for a Discord bot.

This script installs dependencies, prepares the database, fetches data from GitHub,
indexes MyAnimeList data from AnimeAPI, and copies .env.example to .env.

No manual venv setup required - just run the script and it will handle everything:
    uv run firstRun.py     # Recommended
    python3 firstRun.py    # Fallback (requires pip)

Example: uv run firstRun.py
"""

import asyncio
import os
import shlex
import subprocess

from modules.oobe.commons import (
    check_termux,
    current_os,
    is_uv,
    py_bin_path,
)


class FirstRunError(Exception):
    """An exception class for first run script."""


async def first_run(py_bin: str = py_bin_path()):
    """
    Runs the first run script.

    Args:
        py_bin (str, optional): Path to the Python binary. Defaults to py_bin_path().

    Returns:
        None

    Raises:
        Exception: If the script is not run from the root directory.
    """
    # Check if the script is run from the root directory
    if not os.path.exists("requirements.txt"):
        raise FirstRunError("Please run the script from the repo's directory.")
    match os.name:
        case "nt":
            safe_path = py_bin
        case _:
            safe_path = shlex.quote(py_bin)

    # Install/upgrade dependencies
    try:
        # Check if Termux is used
        env = os.environ.copy()
        if check_termux():
            env["MATHLAB"] = "m"
        print(
            "Installing and upgrading dependencies for the next step and the bot itself..."
        )
        if is_uv():
            proc_args = ["uv", "sync", "--upgrade"]
        else:
            proc_args = [
                safe_path,
                "-m",
                "pip",
                "install",
                "-U",
                "-r",
                "requirements.txt",
            ]
        if current_os() == "Windows":
            subprocess.run(proc_args, check=True)
        else:
            subprocess.run(proc_args, check=True, env=env)

    except subprocess.CalledProcessError:
        print("\033[31mError installing packages, please run following command:")
        if is_uv():
            command = "uv sync --upgrade"
        else:
            command = "pip install -U -r requirements.txt"
        if check_termux():
            command = "MATHLAB=m " + command
        print(f"{command}\033[0m")

    # Import modules that depend on installed packages
    from modules.oobe.commons import prepare_database
    from modules.oobe.getNekomimi import nk_run
    from modules.oobe.malIndexer import mal_run
    from modules.oobe.migrate import migrate

    # create a dummy file named cache/dict_installed, if it doesn't exist
    if not os.path.exists("cache/dict_installed"):
        print("Installing unidic dictionary from NINJAL...")
        try:
            subprocess.run(
                [
                    safe_path,
                    "-m",
                    "unidic",
                    "download",
                ],
                check=True,
            )
            with open("cache/dict_installed", "w", encoding="utf8") as file:
                file.write("")
        except subprocess.CalledProcessError:
            print(
                "\033[31mError installing unidic dictionary, please run following command:"
            )
            print(f"{safe_path} -m unidic download\033[0m")

    # Prepare the database
    print("Preparing the database as database.csv in tabbed format...")
    prepare_database()

    # Fetch data from GitHub
    print("Fetching the latest github:nattadasu/nekomimiDb data...")
    await nk_run()

    # Index MyAnimeList data from AnimeAPI
    print("Indexing MyAnimeList data from AnimeAPI...")
    await mal_run()

    # Migrate the database
    print("Migrating database to new schema...")
    await migrate()

    # Import backup option
    if os.isatty(0):
        print("\nDo you have a backup to import? (y/N) ")
        choice = input().lower()
        if choice == "y":
            print("Please enter the path/url to the backup file (.enc):")
            backup_file = input().strip()
            print("Please enter the encryption key:")
            backup_key = input().strip()

            if backup_file and backup_key:
                from import_backup import import_backup as import_func

                await import_func(backup_file, backup_key)
            else:
                print("Invalid input, skipping backup import...")
    else:
        print("Non-interactive mode, skipping backup import...")

    # Check if .env exists, if not, copy .env.example
    if not os.path.exists(".env"):
        print("Copying .env.example to .env...")
        if current_os() == "Windows":
            os.system("copy .env.example .env")
        else:
            os.system("cp .env.example .env")
    else:
        print(".env already exists, skipping...")

    print("Initialization finished. You should be able to run the bot safely now.")


if __name__ == "__main__":
    asyncio.run(first_run())
