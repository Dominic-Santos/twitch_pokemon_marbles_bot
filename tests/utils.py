import json

def load_data(filepath):
    try:
        return json.load(open(filepath))
    except:
        print(f"failed to load {filepath}")
    return {}


def load_mission_data(filename):
    return load_data(f"tests/mission_data/{filename}.json")


def load_inventory_data(filename):
    return load_data(f"tests/inventory_data/{filename}.json")


def load_pokedex():
    return load_data(f"tests/pokedex.json")
