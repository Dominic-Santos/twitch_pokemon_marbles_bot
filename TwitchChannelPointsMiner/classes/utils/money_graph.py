import matplotlib.pyplot as plt
from dateutil.parser import parse
import matplotlib.dates as mdates
from time import sleep

from ..entities.Pokemon.Utils import load_from_file, save_to_file
from ..ChatUtils import DISCORD_STATS

DATA_FILE = "money_graph_data.json"
OUTPUT_IMAGE = "money_graph.png"
MESSAGES_URL = f"{DISCORD_STATS}?limit=50"

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


def load_data(discord):
    data = load_from_file(DATA_FILE)

    msg = None
    limit = "1999-01-01" if data == {} else max([max(data[user].keys()) for user in data.keys()])
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

    save_to_file(DATA_FILE, data)

    return data


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

        usernames = []
        for i, user in enumerate(sorted(self.data.keys())):
            colors = COLORS[i]
            data = self.data[user]
            usernames.append(user)

            self.ax.plot(data["timestamps"], data["cash"], lw=2, color=colors[1])
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))

        self.ax.legend(usernames)

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
            self.data[user]["cash"] = [d[1] for d in sorted_data]

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
