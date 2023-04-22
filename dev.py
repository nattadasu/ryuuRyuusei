#!/usr/bin/env python3

import json
import os
import subprocess

import isort


def print_file(path_name: str) -> None:
    """Prints the file name.

    Args:
        path_name (str): The path name of the file.

    Returns:
        None
    """
    print(f'Formatting file: {path_name}')
    return None


# for each py files exclude from specific folders, sort import
excluded_folders = ['jikanpy', 'venv', '__pycache__', '.vscode']

for root, dirs, files in os.walk('.'):
    # exclude the folders in the excluded_folders list
    dirs[:] = [d for d in dirs if d not in excluded_folders]

    for file in files:
        if file.endswith('.py'):
            print_file(file)
            file_path = os.path.join(root, file)

            # sort imports in the file
            isort.file(file_path)

            # format the file using autopep8
            subprocess.run(['autopep8', '--in-place',
                           '--aggressive', '--aggressive', file_path])

        elif file.endswith('.json'):
            print_file(file)
            file_path = os.path.join(root, file)
            with open(file_path, 'r+') as f:
                data = json.load(f)
                f.seek(0)
                json.dump(data, f, indent=2)
                f.truncate()
