import logging
import os

from .ChatO import logger

if os.path.exists("logs") is False:
    os.makedirs("logs")

LOGFILE = "logs/pokemoncg.txt"

formatter = logging.Formatter('%(asctime)s %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
file_handler = logging.FileHandler(LOGFILE, encoding='utf-8')
file_handler.setFormatter(formatter)
poke_logger = logging.getLogger(__name__ + "pokemon")
poke_logger.setLevel(logging.DEBUG)
poke_logger.addHandler(file_handler)

REDLOG = "\x1b[31;20m"
GREENLOG = "\x1b[32;20m"
YELLOWLOG = "\x1b[36;20m"

LOG_COLORS = {
    "red": REDLOG,
    "yellow": YELLOWLOG,
    "green": GREENLOG
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
