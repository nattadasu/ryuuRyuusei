import json as j
import os
import pathlib

import yaml as y
from langcodes import Language as lang


def convertLangsToJson():
    # loop i18n folder and convert all yaml files to json
    indexed = []
    i18n_dir = pathlib.Path("i18n")
    files = [f for f in i18n_dir.glob("*.yaml") if f.name != "_index.yaml"]
    for file in files:
        with file.open("r", encoding='utf-8') as f:
            data = y.load(f, Loader=y.FullLoader)
            print(f"Converting {file.name} to json", end="")
            code = file.stem
            match code:
                case "lol_US":
                    drip = {
                        'code': code,
                        'name': 'English Lolcat',
                        'native': 'LOLCAT',
                        'dialect': 'United States',
                    }
                case "ace_ID":
                    drip = {
                        'code': code,
                        'name': 'Achinese',
                        'native': 'Acèh',
                        'dialect': 'Indonesia',
                    }
                case _:
                    drip = {
                        'code': code,
                        'name': lang.get(code).language_name(),
                        'native': lang.get(code).language_name(lang.get(code).language),
                        'dialect': lang.get(code).territory_name(),
                    }
            data['meta'] = drip
            indexed.append(drip)
            print(
                f"\rConverted {file.name}: {indexed[-1]['name']} ({indexed[-1]['dialect']}) to json", end="\n")
        with file.with_suffix(".json").open("w", encoding='utf-8', newline='\n') as f:
            j.dump(data, f, indent=2, ensure_ascii=False)
    with (i18n_dir / "_index.json").open("w", encoding='utf-8', newline='\n') as f:
        j.dump(indexed, f, indent=2, ensure_ascii=False)
    print("Indexing languages")
    # sort by code, ignore case
    indexed.sort(key=lambda x: x['code'].lower())
    with open(os.path.join("i18n", "_index.json"), "w", encoding='utf-8', newline='\n') as f:
        j.dump(indexed, f, indent=2, ensure_ascii=False)
    with open(os.path.join("i18n", "_index.yaml"), "w", encoding='utf-8', newline='\n') as f:
        y.dump(indexed, f, indent=2, allow_unicode=True)


if __name__ == "__main__":
    convertLangsToJson()
