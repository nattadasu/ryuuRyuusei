import json as j
import pathlib
from typing import List

import yaml as y
from langcodes import Language as lang


def index_json_lang() -> None:
    """
    Index all JSON files in the i18n folder to dedicated index file.

    Raises:
        FileNotFoundError: If the i18n folder does not exist.

    Returns:
        None.
    """
    i18n_dir = pathlib.Path("i18n")
    if not i18n_dir.exists():
        raise FileNotFoundError("i18n folder does not exist")

    indexed: List[dict] = []
    files = [f for f in i18n_dir.glob("*.json") if f.name != "_index.json"]
    for i, file in enumerate(files):
        i += 1
        with file.open("r", encoding="utf-8") as f:
            code = file.stem
            print(f"[{i}/{len(files)}] Converting {code} to JSON", end="")
            match code:
                case "lol_US":
                    drip = {
                        "code": code,
                        "name": "English Lolcat",
                        "native": "LOLCAT",
                        "dialect": "United States",
                    }
                case "ace_ID":
                    drip = {
                        "code": code,
                        "name": "Achinese",
                        "native": "Acèh",
                        "dialect": "Indonesia",
                    }
                case "sr_SP":
                    drip = {
                        "code": code,
                        "name": "Serbian Cyrillic",
                        "native": "Српски",
                        "dialect": "Serbia",
                    }
                case _:
                    drip = {
                        "code": code,
                        "name": lang.get(code).language_name(),
                        "native": lang.get(code).language_name(
                            lang.get(code).language),
                        "dialect": lang.get(code).territory_name(),
                    }
            indexed.append(drip)
            print(
                f"\r[{i}/{len(files)}] Added {code} ({indexed[-1]['name']} ({indexed[-1]['dialect']})) to Index file",
                end="\n",
            )

    # Create index of languages
    print("Indexing languages")
    indexed.sort(key=lambda x: x["code"].lower())
    with (i18n_dir / "_index.json").open("w", encoding="utf-8", newline="\n") as f:
        j.dump(indexed, f, indent=2, ensure_ascii=False)


def convert_langs_to_json() -> None:
    """
    Convert all YAML files in the i18n folder to JSON format and create an index of languages.
    Raises:
        FileNotFoundError: If the i18n folder does not exist.

    Returns:
        None.
    """
    i18n_dir = pathlib.Path("i18n")
    if not i18n_dir.exists():
        raise FileNotFoundError("i18n folder does not exist")

    indexed: List[dict] = []
    files = [f for f in i18n_dir.glob("*.yaml") if f.name != "_index.yaml"]
    for file in files:
        with file.open("r", encoding="utf-8") as f:
            data = y.safe_load(f)
            print(f"Converting {file.name} to JSON", end="")
            code = file.stem
            match code:
                case "lol_US":
                    drip = {
                        "code": code,
                        "name": "English Lolcat",
                        "native": "LOLCAT",
                        "dialect": "United States",
                    }
                case "ace_ID":
                    drip = {
                        "code": code,
                        "name": "Achinese",
                        "native": "Acèh",
                        "dialect": "Indonesia",
                    }
                case "sr_SP":
                    drip = {
                        "code": code,
                        "name": "Serbian Cyrillic",
                        "native": "Српски",
                        "dialect": "Serbia",
                    }
                case _:
                    drip = {
                        "code": code,
                        "name": lang.get(code).language_name(),
                        "native": lang.get(code).language_name(
                            lang.get(code).language),
                        "dialect": lang.get(code).territory_name(),
                    }
            data["meta"] = drip
            indexed.append(drip)
            print(
                f"\rConverted {file.name}: {indexed[-1]['name']} ({indexed[-1]['dialect']}) to JSON",
                end="\n",
            )
        with file.with_suffix(".json").open("w", encoding="utf-8", newline="\n") as f:
            j.dump(data, f, indent=2, ensure_ascii=False)

    # Create index of languages
    print("Indexing languages")
    indexed.sort(key=lambda x: x["code"].lower())
    with (i18n_dir / "_index.json").open("w", encoding="utf-8", newline="\n") as f:
        j.dump(indexed, f, indent=2, ensure_ascii=False)
    with (i18n_dir / "_index.yaml").open("w", encoding="utf-8", newline="\n") as f:
        y.dump(indexed, f, indent=2, allow_unicode=True)


if __name__ == "__main__":
    convert_langs_to_json()
