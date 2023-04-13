import yaml as y
import json as j
import os

def convertLangsToJson():
    # loop i18n folder and convert all yaml files to json
    for root, dirs, files in os.walk("i18n"):
        for file in files:
            if file.endswith(".yaml"):
                with open(os.path.join(root, file), "r", encoding='utf-8') as f:
                    data = y.load(f, Loader=y.FullLoader)
                    if file != "_index.yaml":
                        print(f"Converting {file} ({data['meta']['native']}) to json")
                    else:
                        print(f"Converting Index file to json")
                with open(os.path.join(root, file).replace(".yaml", ".json"), "w", encoding='utf-8', newline='\n') as f:
                    j.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    convertLangsToJson()
