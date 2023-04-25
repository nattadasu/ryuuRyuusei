import os
import platform
import subprocess


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

    def ask_python(shell_output: str) -> bool:
        """Directly ask Python what version it is"""
        so = shell_output.split(" ")
        v = so[1].split(".")
        # return True if version >= 3.10, False otherwise
        if (int(v[0]) >= 3) and (int(v[1]) >= 10):
            return True
        return False

    if current_os() == "Windows":
        try:
            py = subprocess.check_output("python --version", shell=True).decode("utf-8")
            if ask_python(py):
                return "python"
            raise subprocess.CalledProcessError()
        except subprocess.CalledProcessError:
            paths = subprocess.check_output("where python", shell=True).decode("utf-8")
            paths = paths.replace("\r", "").split("\n")
            # reverse the list, so we can get the up to date python version
            paths.reverse()
            # if index 0 is '', drop it
            if paths[0] == "":
                paths = paths[1:]
            for path in paths:
                p = path.split("\\")
                # Check if version is >= 3.10
                if int(p[-2].replace("Python", "")) >= 310:
                    return path

            return "python"
    else:
        try:
            py3 = subprocess.check_output("python3 --version", shell=True).decode(
                "utf-8"
            )
            if ask_python(py3):
                return "python3"
            raise subprocess.CalledProcessError()
        except subprocess.CalledProcessError:
            py = subprocess.check_output("python --version", shell=True).decode("utf-8")
            if ask_python(py):
                return "python"
            raise Exception("Python version is too old")


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
    files = [
        {
            "path": "database/database.csv",
            "header": "discordId\tdiscordUsername\tdiscordJoined\tmalUsername\tmalId\tmalJoined\tregisteredAt\tregisteredGuild\tregisteredBy",
        },
        {"path": "database/member.csv", "header": "discordId\tlanguage"},
        {"path": "database/server.csv", "header": "guildId\tlanguage"},
    ]

    for file in files:
        if not os.path.exists(file["path"]):
            with open(file["path"], "w") as f:
                f.write(file["header"])
