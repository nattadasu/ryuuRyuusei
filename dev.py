#!/usr/bin/env python3

import asyncio
import json
import os
import subprocess
import sys

import isort

# for each py files exclude from specific folders, sort import
excluded_folders = ["venv", "__pycache__", ".mypycache", "build", "dist", "docs", "cache"]


def print_file(path_name: str) -> None:
    """Prints the file name.

    Args:
        path_name (str): The path name of the file.

    Returns:
        None
    """
    print(f"Formatting file: {path_name}")
    return None


def format_scripts():
    """Formats all python scripts in project file

    Returns:
        None
    """
    for root, dirs, files in os.walk("."):
        # exclude the folders in the excluded_folders list
        dirs[:] = [d for d in dirs if d not in excluded_folders]

        for file in files:
            if file.endswith(".py"):
                print_file(file)
                file_path = os.path.join(root, file)

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
                print_file(file)
                file_path = os.path.join(root, file)
                with open(file_path, "r+") as f:
                    data = json.load(f)
                    f.seek(0)
                    json.dump(data, f, indent=2)
                    f.truncate()


async def loop_test():
    """Do a test for each API calls

    Returns:
        None
    """
    # for each py files in tests folder, test the file using unittest
    for root, dirs, files in os.walk("tests"):
        for file in files:
            if file.endswith(".py"):
                print("Testing " + file)
                file_path = os.path.join(root, file)
                sub = subprocess.Popen([sys.executable, file_path])
                sub.wait()


async def main():
    """Main function of the script

    Return:
        None
    """
    print("Testing API calls found in classes folder")
    await loop_test()

    # ask if user want to format all files
    answer = input("Do you want to format all files? (y/N): ")
    answer = answer.lower() == "y"

    # walk through the current directory
    if answer:
        format_scripts()
    else:
        print("Alright, I won't format the files.")


if __name__ == "__main__":
    asyncio.run(main())
