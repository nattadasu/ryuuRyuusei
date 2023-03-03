#!/usr/bin/env python3

import os
import platform

# check current OS
if platform.system() == "Windows":
    pf = "python"
else:
    pf = "python3"

def installJikanpy():
    # install jikanpy
    print("Installing jikanpy via git...")
    os.system("git clone https://github.com/abhinavk99/jikanpy")
    os.chdir("jikanpy")
    os.system(f"{pf} -m pip install -r requirements.txt")
    os.system(f"{pf} setup.py install")
    os.chdir("..")
    # remove jikanpy folder
    print("Removing jikanpy folder...")
    if platform.system() == "Windows":
        os.system("rmdir /s /q jikanpy")
    else:
        os.system("rm -rf jikanpy")

def checkTermux():
    # check if termux
    if platform.system() == "Linux":
        if os.path.exists("/data/data/com.termux/files/usr/bin"):
            return True
        else:
            return False
    else:
        return False

def main():
    # check if termux
    if checkTermux():
        env = "MATHLAB=\"m\" "
    else:
        env = ""
    # install dependencies
    print("Installing dependencies...")
    os.system(f"{env}{pf} -m pip install -r requirements.txt")
    # run prepFile.py
    print("Running prepFile.py...")
    os.system(f"{pf} firstRun/prepFile.py")
    # run getNekomimi.py
    print("Running getNekomimi.py...")
    os.system(f"{pf} firstRun/getNekomimi.py")
    # run malIndexer.py
    print("Running malIndexer.py...")
    os.system(f"{pf} firstRun/malIndexer.py")
    # check if jikanpy is installed
    try:
        from jikanpy import AioJikan
    except ImportError:
        installJikanpy()
    # reupgrade dependencies that may have been downgraded
    print("Re-upgrading dependencies...")
    os.system(f"{env}{pf} -m pip install -r requirements.txt --upgrade")

if __name__ == "__main__":
    main()
