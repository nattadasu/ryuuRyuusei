import os
import platform
import sys


def current_os() -> str:
    """
    Return the name of the current operating system.

    This function uses the 'platform.system()' method to determine the name of the current operating system.

    Returns:
        str: The name of the current operating system.

    Example:
        >>> current_os()
        'Windows'
    """
    return platform.system()


class UnsupportedOS(Exception):
    """Unsupported operating system."""


class UnsupportedVersion(Exception):
    """Unsupported version of Python."""

    def __init__(self, message: str, version: str):
        super().__init__(message)
        self.version = version


def py_bin_path() -> str:
    """
    Return the path of the Python binary.

    This function checks the version of Python installed and returns the path to the binary for the latest installed version
    that is >= 3.10.

    Returns:
        str: The path of the Python binary.

    Raises:
        Exception: If Python version is too old.

    Example:
        >>> py_bin_path()
        '/usr/local/bin/python3'
    """
    if os.getenv("PYTHON_BINARY"):
        # return the env var if it exists
        return os.getenv("PYTHON_BINARY")

    # get current python version with sys.version_info
    py_version = sys.version_info
    # if python version is >= 3.10, return the path to the binary
    if py_version >= (3, 10):
        return sys.executable
    # if python version is < 3.10, raise an exception
    raise UnsupportedVersion(
        version=sys.version,
        message="Python version is too old.")


pf = py_bin_path()


# check if termux
def check_termux() -> bool:
    """
    Check if the script is running on Termux.

    Returns:
        bool: True if running on Termux, False otherwise.
    """
    return current_os() == "Linux" and os.path.exists(
        "/data/data/com.termux/files/usr/bin"
    )


def prepare_database():
    """
    Prepare the database files for storing user and server information.

    This function checks if the `database/database.csv`, `database/member.csv`, and `database/server.csv` files exist.
    If not, it creates a new file with the corresponding header.

    Returns:
        None
    """
    database_cells = [
        "discordId",
        "discordUsername",
        "discordJoined",
        "malUsername",
        "malId",
        "malJoined",
        "registeredAt",
        "registeredGuildId",
        "registeredBy",
        "registeredGuildName",
        "anilistUsername",
        "anilistId",
        "lastfmUsername",
        "shikimoriId",
        "shikimoriUsername",
    ]
    database_header = "\t".join(database_cells)
    files = [
        {
            "path": "database/database.csv",
            "header": database_header,
        },
        {"path": "database/member.csv", "header": "discordId\tlanguage"},
        {"path": "database/server.csv", "header": "guildId\tlanguage"},
    ]

    for file in files:
        if not os.path.exists(file["path"]):
            with open(file["path"], "w") as f:
                f.write(file["header"])
