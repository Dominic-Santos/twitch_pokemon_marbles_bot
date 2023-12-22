import matplotlib.pyplot as plt
import json
from dateutil.parser import parse
import matplotlib.dates as mdates
from time import sleep

from TwitchChannelPointsMiner.classes.entities.Pokemon.Discord import Discord

SETTINGS_FILE = "pokemon.json"
DATA_FILE = "money_graph_data.json"

DISCORD_BASE = "https://discord.com/api/v9/channels"
CHANNEL = 1142788566590689290
MESSAGES_URL = f"{DISCORD_BASE}/{CHANNEL}/messages?limit=50"


COLORS = [
    ["#910000", "#ff0000", "#be4343", "#ff7878"],
    ["#000091", "#0000ff", "#4343be", "#7878ff"]
]


def parse_message(content):
    try:
        if "Inventory" in content:
            return int(content.split("Inventory: ")[1].split("$")[0])
    except Exception as ex:
        print(ex)
    return None


def load_data():
    data = load_json(DATA_FILE)
    settings = load_json(SETTINGS_FILE)
    discord = Discord()
    discord.set(settings["discord"])
    discord.connect()

    msg = None
    limit = "1999-01-01" if data == {} else max([max(data[user].keys()) for user in data.keys()])
    done = False

    while True:
        if msg is None:
            url = MESSAGES_URL
        else:
            url = MESSAGES_URL + "&before=" + str(msg["id"])

        print(url)
        messages = discord.get(url)
        if len(messages) == 0:
            break

        for msg in messages:
            user = msg["author"]["global_name"]

            res = parse_message(msg["content"])
            if res is None:
                continue

            timestamp = msg["timestamp"]
            if timestamp < limit:
                done = True
            data.setdefault(user, {})[timestamp] = res

        if done:
            break

        sleep(1)

    save_json(data, DATA_FILE)

    return data


def load_json(the_file):
    try:
        with open(the_file, "r") as f:
            j = json.load(f)
            return j
    except:
        pass
    return {}


def save_json(data, the_file):
    with open(the_file, "w") as f:
        json.dump(data, f, indent=4)


class Graph:
    def __init__(self):
        self.ind = 0
        self.mode = 0
        self.modes = []

    def init_graph(self):
        self.fig, self.ax = plt.subplots()
        self.fig.subplots_adjust(bottom=0.2)
        self.load_data()
        self.plot()

    def plot(self, clear=False):
        if clear:
            self.ax.clear()

        for i, user in enumerate(sorted(self.data.keys())):
            colors = COLORS[i]
            data = self.data[user]

            self.ax.plot(data["timestamps"], data["cash"], lw=2, color=colors[1])
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))

    def init_data(self):
        self.data_dirty = load_data()

        self.modes = ["all"]

    def load_data(self):

        self.data = {}

        for user in self.data_dirty:
            user_data = self.data_dirty[user]

            tuple_data = [(k, v) for k, v in user_data.items()]

            sorted_data = sorted(tuple_data, key=lambda x: x[0])

            self.data[user] = {}
            self.data[user]["timestamps"] = [parse(d[0]) for d in sorted_data]
            self.data[user]["cash"] = [d[1] for d in sorted_data]

    def refresh_data(self):
        self.load_data()
        self.plot(clear=True)
        plt.draw()


def main():

    g = Graph()
    g.init_data()
    g.init_graph()

    plt.show()
    print("Done")


if __name__ == "__main__":
    main()
