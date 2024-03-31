import matplotlib.pyplot as plt
from dateutil.parser import parse
import matplotlib.dates as mdates
from time import sleep

from ..entities.Pokemon.Utils import load_from_file, save_to_file
from ..Utils import DISCORD_STATS

DATA_FILE = "catch_graph_data.json"
OUTPUT_IMAGE = "catch_graph.png"
MESSAGES_URL = f"{DISCORD_STATS}?limit=50"

COLORS = [
    ["#910000", "#ff0000", "#be4343", "#ff7878"],
    ["#000091", "#0000ff", "#4343be", "#7878ff"]
]


def parse_message(content):
    try:
        if "Spawnable Pokedex" in content:
            total = float(content.split("Spawnable Pokedex: ")[1].split("(")[1].split("%)")[0])
            a_tier = float(content.split("A: ")[1].split("(")[1].split("%)")[0])
            b_tier = float(content.split("B: ")[1].split("(")[1].split("%)")[0])
            c_tier = float(content.split("C: ")[1].split("(")[1].split("%)")[0])
            return {
                "total": total,
                "a": a_tier,
                "b": b_tier,
                "c": c_tier,
            }
    except Exception as ex:
        print(ex)
    return None


def load_data(discord):
    data = load_from_file(DATA_FILE)

    completed = {}
    prev_data = {}
    msg = None
    limit = "1999-01-01" if data == {} else max(data.keys())
    done = False

    while True:
        if msg is None:
            url = MESSAGES_URL
        else:
            url = MESSAGES_URL + "&before=" + str(msg["id"])

        messages = discord.get(url)
        if len(messages) == 0:
            break

        for msg in messages:
            user = msg["author"]["global_name"]

            if completed.get(user, False):
                continue

            res = parse_message(msg["content"])
            if res is None:
                continue

            timestamp = msg["timestamp"]
            prev = prev_data.get(user, 100.0)

            if timestamp < limit:
                done = True

            if res["total"] > prev:
                completed[user] = True
                continue

            data.setdefault(user, {})[timestamp] = res
            completed[user] = False
            prev_data[user] = res["total"]

        if all(completed.values()) or done:
            break

        sleep(1)

    cleandata = {}

    for user in data:
        prev = 101
        cleandata[user] = {}
        for timestamp in sorted(data[user], reverse=True):
            v = data[user][timestamp]
            if v['total'] > prev:
                break

            cleandata[user][timestamp] = v
            prev = v['total']

    save_to_file(DATA_FILE, cleandata)

    return cleandata


class Graph:
    def __init__(self, discord):
        self.ind = 0
        self.mode = 0
        self.modes = []
        self.discord = discord

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

            self.ax.plot(data["timestamps"], data["total"], lw=2, color=colors[0])
            self.ax.plot(data["timestamps"], data["a"], lw=2, color=colors[1])
            self.ax.plot(data["timestamps"], data["b"], lw=2, color=colors[2])
            self.ax.plot(data["timestamps"], data["c"], lw=2, color=colors[3])
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))

    def init_data(self):
        self.data_dirty = load_data(self.discord)
        self.modes = ["all"]

    def load_data(self):

        self.data = {}

        for user in self.data_dirty:
            user_data = self.data_dirty[user]

            tuple_data = [(k, v) for k, v in user_data.items()]

            sorted_data = sorted(tuple_data, key=lambda x: x[0])

            self.data[user] = {}
            self.data[user]["timestamps"] = [parse(d[0]) for d in sorted_data]
            self.data[user]["total"] = [d[1]["total"] for d in sorted_data]
            self.data[user]["a"] = [d[1]["a"] for d in sorted_data]
            self.data[user]["b"] = [d[1]["b"] for d in sorted_data]
            self.data[user]["c"] = [d[1]["c"] for d in sorted_data]

    def refresh_data(self):
        self.load_data()
        self.plot(clear=True)
        plt.draw()


def create_graph(discord):
    g = Graph(discord)
    g.init_data()
    g.init_graph()


def run_graph(discord):
    create_graph(discord)
    plt.show()


def generate_graph(discord):
    create_graph(discord)
    plt.savefig(OUTPUT_IMAGE)
