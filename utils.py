import json


def load_json_file(filename):
    with open(filename) as f:
        data = json.load(f)
    return data


def load_settings():
    settings = load_json_file("settings.json")
    login = load_json_file("twitch_login.json")
    settings["login"] = login
    return settings
