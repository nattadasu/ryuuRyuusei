#!/usr/bin/env python3

from modules.oobe.commons import *
from modules.oobe.jikan import *
from modules.oobe.malIndexer import *
from modules.oobe.getNekomimi import *
from modules.oobe.i18nBuild import *

def main():
    # check if termux
    if checkTermux():
        env = "MATHLAB=\"m\" "
    else:
        env = ""
    # check if jikanpy is installed
    try:
        from jikanpy import AioJikan
        # using git, fetch latest jikanpy
        # if there's any changes, install it
        print("Checking for jikanpy updates...")
        os.chdir("jikanpy")
        os.system("git pull")
        if os.system("git diff --exit-code origin/master") != 0:
            updateJikanpy()
        os.chdir("..")
    except ImportError:
        installJikanpy()
    # install dependencies
    print("Installing and upgrading dependencies for next step and the bot itself...")
    os.system(f"{env}{pf} -m pip install -U -r requirements.txt")
    # run prepFile.py
    print("Preparing database as database.csv in tabbed format...")
    prepare_database()
    # run getNekomimi.py
    print("Fetching latest github:nattadasu/nekomimiDb data...")
    nk_run()
    # run malIndexer.py
    print("Indexing MyAnimeList data from AnimeAPI...")
    mal_run()
    # check if .env exists, if not, copy .env.example
    if not os.path.exists(".env"):
        print("Copying .env.example to .env...")
        if currentOS() == "Windows":
            os.system("copy .env.example .env")
        else:
            os.system("cp .env.example .env")
    else:
        print(".env already exists, skipping...")
    # build language index
    print("Building language index...")
    convertLangsToJson()
    print("Initialization finished, you should able to run the bot safely now.")

if __name__ == "__main__":
    main()
