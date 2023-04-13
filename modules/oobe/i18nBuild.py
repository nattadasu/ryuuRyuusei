import yaml as y
import json as j
import os

def convertLangsToJson():
    # loop i18n folder and convert all yaml files to json
    indexed = []
    for root, dirs, files in os.walk("i18n"):
        for file in files:
            if file.endswith(".yaml"):
                with open(os.path.join(root, file), "r", encoding='utf-8') as f:
                    data = y.load(f, Loader=y.FullLoader)
                    if file != "_index.yaml":
                        print(f"Converting {file} to json")
                        data['meta']['code'] = file.replace(".yaml", "")
                        indexed += [data['meta']]
                with open(os.path.join(root, file).replace(".yaml", ".json"), "w", encoding='utf-8', newline='\n') as f:
                    j.dump(data, f, indent=2, ensure_ascii=False)
    print("Indexing languages")
    # sort by code, ignore case
    indexed.sort(key=lambda x: x['code'].lower())
    with open(os.path.join("i18n", "_index.json"), "w", encoding='utf-8', newline='\n') as f:
        j.dump(indexed, f, indent=2, ensure_ascii=False)
    with open(os.path.join("i18n", "_index.yaml"), "w", encoding='utf-8', newline='\n') as f:
        y.dump(indexed, f, indent=2, allow_unicode=True)

if __name__ == "__main__":
    convertLangsToJson()
