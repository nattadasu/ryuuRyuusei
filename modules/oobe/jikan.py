import os
import shlex
import subprocess

from .commons import pf


def revert_reqs():
    """
    Revert changes made to the requirements.txt file and discard unstaged changes.

    This function removes the requirements.txt file using the os.remove() method and then runs the command 'git checkout HEAD .'
    to discard any unstaged changes made to the file.

    Args:
        None

    Returns:
        None

    Raises:
        OSError: If the file requirements.txt cannot be removed.

    Example:
        >>> revert_reqs()
    """
    os.remove("requirements.txt")
    os.system("git checkout HEAD .")


def update_jikanpy(pf: str = pf):
    """
    Update the Jikanpy library by removing version locks for aiohttp and requests in the requirements.txt file.

    This function reads the requirements.txt file and removes any version locks for aiohttp and requests libraries.
    It then updates Jikanpy by installing the requirements and the package itself. Finally, it calls the revert_reqs()
    function to revert changes made to the requirements.txt file.

    Args:
        pf (str): The path to the Python executable.

    Returns:
        None

    Example:
        >>> update_jikanpy("python")
    """
    reqs = ""
    with open("requirements.txt", "r") as f:
        # remove version lock for aiohttp and requests
        for line in f.readlines():
            if "aiohttp" in line:
                reqs += "aiohttp\n"
            elif "requests" in line:
                reqs += "requests\n"
            else:
                reqs += line
    with open("requirements.txt", "w") as f:
        f.write(reqs)
    if os.name == "nt":
        subprocess.run(
            [pf, "-m", "pip", "install", "-r", "requirements.txt"], shell=False
        )
    else:
        os.system(
            shlex.join(
                [shlex.quote(pf), "-m", "pip", "install", "-r", "requirements.txt"]
            )
        )
        os.system(shlex.join([shlex.quote(pf), "setup.py", "install"]))
    revert_reqs()


def install_jikanpy(pf: str = pf):
    """
    Install the Jikanpy library from GitHub by cloning the repository and updating its dependencies.

    This function clones the Jikanpy GitHub repository using the 'git clone' command and then changes the current directory
    to the cloned repository. It then calls the 'update_jikanpy()' function to update the package dependencies and finally,
    changes the current directory back to the original directory.

    Args:
        pf (str): The path to the Python executable.

    Returns:
        None

    Example:
        >>> install_jikanpy("python")
    """
    print("Installing Jikanpy via git...")
    os.system("git clone https://github.com/abhinavk99/jikanpy")
    os.chdir("jikanpy")
    update_jikanpy(pf)
    os.chdir("..")
