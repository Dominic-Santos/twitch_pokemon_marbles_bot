from time import sleep
import traceback
from datetime import datetime, timedelta
from dateutil.parser import parse

from ..entities.Pokemon.Pokedaily import parse_next_available, parse_full_message

from ..ChatLogs import log
from ..ChatUtils import (
    DISCORD_ALERTS,
    DISCORD_POKEDAILY,
    DISCORD_POKEDAILY_SEARCH,
    POKEDAILY_DELAY,
    POKEMON,
    seconds_readable,
)

SLEEPTIME = 30
ATTEMPTS_LIMIT = 10


class Pokedaily(object):
    def get_next_pokedaily(self):
        resp = POKEMON.discord.get(DISCORD_POKEDAILY_SEARCH.format(discord_id=POKEMON.discord.data["user"]))
        latest_message = resp["messages"][0][0]

        next_available = parse_next_available(latest_message["content"])
        timestamp = parse(latest_message["timestamp"])
        now = datetime.now()

        if next_available == 0:
            next_redeem = int(POKEDAILY_DELAY - (now.timestamp() - timestamp.timestamp()))
        else:
            next_redeem = int(timestamp.timestamp() + next_available - now.timestamp())
        return next_redeem

    def pokedaily_timer(self):
        thread_name = "Pokedaily Timer"
        max_wait = 60 * 60  # 1 hour
        log("yellow", f"Thread Created - {thread_name}")

        running = True
        exit = False
        remaining_time = 0

        while running and exit is False:
            try:
                remaining_time = self.get_next_pokedaily()
                running = False
            except KeyboardInterrupt:
                exit = True
            except Exception as ex:
                str_ex = str(ex)
                log("red", f"{thread_name} Error - {str_ex}")
                print(traceback.format_exc())
                sleep(5)

        while exit is False:
            while remaining_time > 0:
                remaining_human = seconds_readable(remaining_time)
                log("yellow", f"{thread_name} - Waiting for {remaining_human}")
                wait = min(max_wait, remaining_time)
                sleep(wait)
                remaining_time -= wait

            try:
                self.pokedaily()
                remaining_time = POKEDAILY_DELAY
            except KeyboardInterrupt:
                exit = True
            except Exception as ex:
                remaining_time = 5
                str_ex = str(ex)
                log("red", f"{thread_name} Error - {str_ex}")
                print(traceback.format_exc())

        log("yellow", f"Thread Closing - {thread_name}")

    def pokedaily(self):
        self.update_inventory()

        log("yellow", f"Running Pokedaily")
        POKEMON.discord.post(DISCORD_POKEDAILY, "!pokedaily")

        if POKEMON.discord.data["user"] is None:
            POKEMON.discord.post(DISCORD_ALERTS, "Pokedaily, no user configured")
            log("green", f"Pokedaily, no user configured")
            return

        attempts = 0
        while attempts < ATTEMPTS_LIMIT:
            sleep(SLEEPTIME)
            log("yellow", f"Looking for Pokedaily answer")
            resp = POKEMON.discord.get(DISCORD_POKEDAILY_SEARCH.format(discord_id=POKEMON.discord.data["user"]))
            msg = resp["messages"][0][0]
            message = parse_full_message(msg)

            if datetime.now() - message.timestamp < timedelta(minutes=10):
                # found the message was looking for
                break

        if attempts == ATTEMPTS_LIMIT:
            slept = SLEEPTIME * ATTEMPTS_LIMIT
            log("red", f"Failed to get answer from Pokedaily after {slept} seconds")
        elif message.repeat:
            log("red", f"Pokedaily not ready")
        else:
            POKEMON.discord.post(DISCORD_ALERTS, f"Pokedaily rewards ({message.rarity}):\n" + "\n".join(message.rewards))
            log("green", f"Pokedaily ({message.rarity}) rewards " + ", ".join(message.rewards))

        self.update_inventory(skip=True)
