from datetime import timedelta
from threading import Thread

from .entities.Pokemon import PokemonComunityGame

ITEM_MIN_AMOUNT = 10
ITEM_MIN_PURCHASE = 10

MARBLES_DELAY = 60 * 3  # seconds
MARBLES_TRIGGER_COUNT = 3
WONDERTRADE_DELAY = 60 * 60 * 3 + 60  # 3 hours and 1 min (just in case)
POKEDAILY_DELAY = 60 * 60 * 20 + 60  # 20 hours and 1 min


REDLOG = "\x1b[31;20m"
GREENLOG = "\x1b[32;20m"
YELLOWLOG = "\x1b[36;20m"

LOG_COLORS = {
    "red": REDLOG,
    "yellow": YELLOWLOG,
    "green": GREENLOG
}

ALERTS_CHANNEL = 1072557550526013440
STATS_CHANNEL = 1142788566590689290
POKEDAILY_CHANNEL = 800433942695247872
COMMANDS_CHANNEL = 1169286325279670332
POKEDAILY_GUILD = 711921837503938640
MARZSERVER_GUILD = 875913576106328084

POKEMON = PokemonComunityGame()

DISCORD_BASE = "https://discord.com/api/v9/"
DISCORD_ALERTS = f"{DISCORD_BASE}channels/{ALERTS_CHANNEL}/messages"
DISCORD_STATS = f"{DISCORD_BASE}channels/{STATS_CHANNEL}/messages"
DISCORD_POKEDAILY = f"{DISCORD_BASE}channels/{POKEDAILY_CHANNEL}/messages"
DISCORD_POKEDAILY_SEARCH = f"{DISCORD_BASE}guilds/{POKEDAILY_GUILD}/messages/search?channel_id={POKEDAILY_CHANNEL}&mentions=" + "{discord_id}"
DISCORD_COMMANDS_SEARCH = f"{DISCORD_BASE}guilds/{MARZSERVER_GUILD}/messages/search?channel_id={COMMANDS_CHANNEL}&author_id=" + "{discord_id}"
DISCORD_DELETE_COMMAND = f"{DISCORD_BASE}channels/{COMMANDS_CHANNEL}/messages/" + "{message_id}"

POKEMON.set_alerts(True, DISCORD_ALERTS)

CHARACTERS = {
    "starter": "⭐",
    "female": "♀",
    "legendary": "💪"
}


def _clean_text(level, text):
    if level in LOG_COLORS:
        color = LOG_COLORS[level]
        return f"{color}{text}"
    return text


def seconds_readable(seconds):
    return str(timedelta(seconds=seconds)).split(".")[0]


class ThreadController(object):
    def __init__(self):
        self.client_channel = None
        self.clients = {}
        self.started = False

    def remove_client(self, channel):
        self.clients.pop(channel, None)
        if self.client_channel == channel:
            self.client_channel = None

    def chose_client(self):
        client_keys = list(self.clients.keys())
        if len(client_keys) > 0:
            self.client_channel = client_keys[0]

    def get_client(self):
        if self.client_channel is None:
            self.chose_client()

        return self.client_channel, self.clients.get(self.client_channel, None)


THREADCONTROLLER = ThreadController()


def create_thread(func):
    worker = Thread(target=func)
    worker.setDaemon(True)
    worker.start()

def get_pokemon():
    return POKEMON

def leave_channel(channel):
    if channel in POKEMON.channel_list:
        POKEMON.remove_channel(channel)
        log(text=f"Leaving Pokemon: {channel}")
        if len(POKEMON.channel_list) == 0:
            log_file(text="Nobody is streaming Pokemon CG")

    if channel in POKEMON.online_channels:
        POKEMON.channel_offline(channel)

    THREADCONTROLLER.remove_client(channel)