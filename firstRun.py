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

def main():
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
        import jikanpy
    except ImportError:
        installJikanpy()

if __name__ == "__main__":
    main()
