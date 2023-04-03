#!/usr/bin/env python3

from modules.oobe.commons import *

MAIN_SITE = "https://raw.githubusercontent.com/nattadasu/nekomimiDb/main/index.tsv"

def nk_get_data():
    data = r.get(MAIN_SITE).text
    # save data to file
    with open("database/nekomimiDb.tsv", "w") as f:
        f.write(data)


def nk_run():
    if not os.path.exists("database/nekomimiDb.tsv"):
        nk_get_data()
    else:
        # check if the file is >= 14 days old
        if os.stat("database/nekomimiDb.tsv").st_mtime < (time.time() - 14 * 86400):
            nk_get_data()
