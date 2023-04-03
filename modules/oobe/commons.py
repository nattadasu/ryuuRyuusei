import json
import os
import platform
import time
import re

import pandas as pd
import requests as r
import subprocess as sub


# check current OS
def currentOS() -> str:
    """Return current OS"""
    return platform.system()


def pyBinPath() -> str:
    """Return python binary path"""
    if os.getenv("PYTHON_BINARY"):
        # eh, just return the env var if it exists
        return os.getenv("PYTHON_BINARY")
    def askPython(shellOutput: str) -> bool:
        """Directly ask Python what version it is"""
        so = shellOutput.split(" ")
        v = so[1].split(".")
        # return python if version >= 3.9
        if (int(v[0]) >= 3) and (int(v[1]) >= 9):
            return True
        else:
            return False
    if currentOS() == "Windows":
        try:
            py = sub.check_output("python --version", shell=True).decode("utf-8")
            if askPython(py):
                return "python"
            else:
                raise sub.CalledProcessError()
        except sub.CalledProcessError:
            paths = sub.check_output("where python", shell=True).decode("utf-8")
            paths = paths.replace('\r','').split("\n")
            # reverse the list, so we can get the up to date python version
            paths.reverse()
            # if index 0 is '', drop it
            if paths[0] == "":
                paths = paths[1:]
            for path in paths:
                p = path.split("\\")
                # Check if version is >= 3.9
                if int(p[-2].replace("Python", "")) >= 39:
                    return path
            else:
                return "python"
    else:
        try:
            py3 = sub.check_output("python3 --version", shell=True).decode("utf-8")
            if askPython(py3):
                return "python3"
            else:
                raise sub.CalledProcessError()
        except sub.CalledProcessError:
            py = sub.check_output("python --version", shell=True).decode("utf-8")
            if askPython(py):
                return "python"
            else:
                raise Exception("Python version is too old")


pf = pyBinPath()


# check if termux
def checkTermux() -> bool:
    """Check if the script is running on Termux"""
    if currentOS() == "Linux":
        if os.path.exists("/data/data/com.termux/files/usr/bin"):
            return True
        else:
            return False
    else:
        return False


def prepare_database():
    """Prepare database.csv file with pre-defined header"""
    # check if the file database/database.csv exists
    if not os.path.exists("database/database.csv"):
        # if not, write new header
        with open("database/database.csv", "w") as f:
            f.write("discordId\tdiscordUsername\tdiscordJoined\tmalUsername\tmalId\tmalJoined\tregisteredAt\tregisteredGuild\tregisteredBy")
