from modules.oobe.commons import *


def revertReqs():
    os.remove("requirements.txt")
    os.system("git checkout HEAD .")


def updateJikanpy():
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
    os.system(f"{pf} -m pip install -r requirements.txt")
    os.system(f"{pf} setup.py install")
    revertReqs()


def installJikanpy():
    # install jikanpy
    print("Installing jikanpy via git...")
    os.system("git clone https://github.com/abhinavk99/jikanpy")
    os.chdir("jikanpy")
    updateJikanpy()
    os.chdir("..")
