#!/usr/bin/env python3

from modules.oobe.commons import *

# encode ( and ) to %28 and %29
MAIN_SITE = 'https://aniapi.nattadasu.my.id/myanimelist%28%29.json'


def mal_get_data():
    data = r.get(MAIN_SITE)
    # save data to json file
    with open("cache/mal.json", "w", encoding="utf8") as f:
        json.dump(data.json(), f, ensure_ascii=False)


def mal_load_data():
    with open("cache/mal.json", "r") as f:
        data = json.load(f)
    return data


def mal_run():
    if not os.path.exists("cache/mal.json"):
        mal_get_data()
    else:
        # check if the file is >= 14 days old
        if os.stat("cache/mal.json").st_mtime < (time.time() - 14 * 86400):
            mal_get_data()
    data = mal_load_data()
    df = pd.DataFrame(data)
    # only select title and myAnimeList columns
    df = df[["myanimelist", "title"]]
    # rename myAnimeList to mal_id
    df.rename(columns={"myanimelist": "mal_id"}, inplace=True)
    # sort by mal_id
    df.sort_values(by="mal_id", inplace=True)
    # save to csv file with utf-8 encoding and \t as delimiter
    df.to_csv("database/mal.csv", encoding="utf-8", sep="\t", index=False)
