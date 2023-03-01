#!/usr/bin/env python3

import os
import requests as r
import time

MAIN_SITE = "https://raw.githubusercontent.com/nattadasu/nekomimiDb/main/index.tsv"

def get_data():
    data = r.get(MAIN_SITE).text
    # save data to file
    with open("database/nekomimiDb.tsv", "w") as f:
        f.write(data)


def main():
    if not os.path.exists("database/nekomimiDb.tsv"):
        get_data()
    else:
        # check if the file is >= 14 days old
        if os.stat("database/nekomimiDb.tsv").st_mtime < (time.time() - 14 * 86400):
            get_data()

if __name__ == "__main__":
    main()
