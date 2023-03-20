import json


def load_json_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.loads(f.read())


def dump_as_json(msg, dct):
    print(f"{msg}:")
    print(json.dumps(dct,indent=2)+"\n")
