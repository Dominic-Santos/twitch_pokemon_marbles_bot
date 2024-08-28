import json


def load_json_file(filename):
    with open(filename) as f:
        data = json.load(f)
    return data

def get_login():
    login = load_json_file("twitch_login.json")
    return login


def load_settings():
    settings = load_json_file("settings.json")
    return settings
