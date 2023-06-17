import json


def load_settings(filename="settings.json"):
    with open(filename) as f:
        settings = json.load(f)
    return settings
