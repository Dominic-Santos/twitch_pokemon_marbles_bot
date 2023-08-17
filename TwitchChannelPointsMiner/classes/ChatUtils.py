import logging
import os

from .ChatO import logger

from .entities.Pokemon import PokemonComunityGame

if os.path.exists("logs") is False:
    os.makedirs("logs")

LOGFILE = "logs/pokemoncg.txt"

formatter = logging.Formatter('%(asctime)s %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
file_handler = logging.FileHandler(LOGFILE, encoding='utf-8')
file_handler.setFormatter(formatter)
poke_logger = logging.getLogger(__name__ + "pokemon")
poke_logger.setLevel(logging.DEBUG)
poke_logger.addHandler(file_handler)

ITEM_MIN_AMOUNT = 10
ITEM_MIN_PURCHASE = 10

MARBLES_DELAY = 60 * 3  # seconds
MARBLES_TRIGGER_COUNT = 3

REDLOG = "\x1b[31;20m"
GREENLOG = "\x1b[32;20m"
YELLOWLOG = "\x1b[36;20m"

LOG_COLORS = {
    "red": REDLOG,
    "yellow": YELLOWLOG,
    "green": GREENLOG
}

ALERTS_CHANNEL = 1072557550526013440
STATS_CHANNEL = 1137163122063450162
POKEDAILY_CHANNEL = 800433942695247872
POKEDAILY_GUILD = 711921837503938640

POKEMON = PokemonComunityGame()

DISCORD_BASE = "https://discord.com/api/v9/"
DISCORD_ALERTS = f"{DISCORD_BASE}channels/{ALERTS_CHANNEL}/messages"
DISCORD_STATS = f"{DISCORD_BASE}channels/{STATS_CHANNEL}/messages"
DISCORD_POKEDAILY = f"{DISCORD_BASE}channels/{POKEDAILY_CHANNEL}/messages"
DISCORD_POKEDAILY_SEARCH = f"{DISCORD_BASE}guilds/{POKEDAILY_GUILD}/messages/search?channel_id={POKEDAILY_CHANNEL}&mentions=" + "{discord_id}"

FISH_EVENT = False

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


def log(level="none", text=""):
    logger.info(_clean_text(level, text), extra={"emoji": ":speech_balloon:"})


def log_file(level="none", text=""):
    poke_logger.info(_clean_text(level, text))
