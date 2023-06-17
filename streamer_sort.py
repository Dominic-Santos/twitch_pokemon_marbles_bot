from utils import load_settings
import json


def jstring(s):
    return s.replace("'", '"')


def get_current_points(username, streamer):
    try:
        with open(f'analytics/{username}/{streamer}.json') as f:
            streamer_data = json.load(f)
        return streamer_data["series"][-1]["y"]
    except:
        return 0
    return 0


def format_streamer(username, name, data):
    data["points"] = get_current_points(username, name)
    data["percent"] = int(data["points"] / data["goal"] * 100)
    return jstring(str(data)).replace("True", "true")


def main(settings=None, filename="settings.json"):
    if settings is None:
        settings = load_settings(filename)
    streamers = settings["streamers"]
    username = settings["username"]
    streamers_ordered = sorted(streamers.keys(), key=lambda x: (streamers[x]["priority"], streamers[x]["goal"], get_current_points(username, x) * - 1))
    other_settings = [k for k in settings.keys() if k != "streamers"]

    with open(filename, "w") as f:
        f.write('{\n    "streamers": {\n')
        streamers = ",\n".join([f'        "{streamer}": ' + format_streamer(username, streamer, streamers[streamer]) for streamer in streamers_ordered])
        f.write(streamers + "\n")
        f.write("    }")
        if len(other_settings) > 0:
            f.write(",")
        f.write("\n")

        for i, v in enumerate(other_settings):
            f.write(f'    "{v}": ' + jstring(repr(settings[v])))
            if i != len(other_settings) - 1:
                f.write(",")
            f.write("\n")

        f.write("}\n")


if __name__ == "__main__":
    main()
