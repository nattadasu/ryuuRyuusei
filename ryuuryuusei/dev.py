#!/usr/bin/env python3

import asyncio
import json
import os
import subprocess
import sys

import isort

# for each py files exclude from specific folders, sort import
excluded_folders = [
    "venv",
    "__pycache__",
    ".mypycache",
    ".mypy_cache",
    "build",
    "dist",
    "docs",
    "cache",
]
"""List of folders to exclude from formatting"""


def print_file(path_name: str) -> None:
    """
    Prints the file name.

    Args:
        path_name (str): The path name of the file.

    Returns:
        None
    """
    print(f"Formatting file: {path_name}")
    return None


def format_scripts():
    """
    Formats all python scripts in project file

    Returns:
        None
    """
    for root, dirs, files in os.walk("."):
        # exclude the folders in the excluded_folders list
        dirs[:] = [d for d in dirs if d not in excluded_folders]

        for file in files:
            if file.endswith(".py"):
                # print full path of the file
                file_path = os.path.join(root, file)
                print_file(file_path)

                # sort imports in the file
                isort.file(file_path)

                # format the file using autopep8
                subprocess.run(
                    [
                        "autopep8",
                        "--in-place",
                        "--aggressive",
                        "--aggressive",
                        file_path,
                    ],
                    check=True,
                )

            elif file.endswith(".json"):
                file_path = os.path.join(root, file)
                print_file(file_path)
                with open(file_path, "r+") as f:
                    data = json.load(f)
                    f.seek(0)
                    json.dump(data, f, indent=2)
                    f.truncate()


async def loop_test():
    """
    Do a test for each API calls

    Returns:
        None
    """
    sub = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "coverage",
            "run",
        ]
    )
    sub.wait()
    sub = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "coverage",
            "report",
        ]
    )
    sub.wait()
    sub = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "coverage",
            "xml",
        ]
    )
    sub.wait()


async def main():
    """
    Main function of the script

    Return:
        None
    """
    answer_test = input("Do you want to test all API calls? (y/N): ")
    answer_test = answer_test.lower() == "y"
    if answer_test:
        print("Testing API calls found in classes folder")
        await loop_test()
    else:
        print("Alright, I won't test the API calls.")

    # ask if user want to format all files
    answer_format = input("Do you want to format all files? (y/N): ")
    answer_format = answer_format.lower() == "y"

    # walk through the current directory
    if answer_format:
        format_scripts()
    else:
        print("Alright, I won't format the files.")


if __name__ == "__main__":
    asyncio.run(main())
