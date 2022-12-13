
import json
import os


def read_from_json(path: os.path) -> dict:

    with open(path, 'r') as aanbod_json:

        aanbod = json.load(aanbod_json)
        aanbod_json.close()

    return aanbod


def write_to_json(path: os.path, data: dict) -> None:

    with open(path, 'w') as aanbod_json:

        json.dump(data, aanbod_json)
        aanbod_json.close()

    return None
