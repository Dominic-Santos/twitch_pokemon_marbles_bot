from time import sleep
import traceback
from datetime import datetime
from dateutil.parser import parse

from ..entities.Pokemon.Pokedaily import parse_next_available, parse_message

from ..ChatUtils import (
    DISCORD_ALERTS,
    DISCORD_POKEDAILY,
    DISCORD_POKEDAILY_SEARCH,
    log,
    POKEDAILY_DELAY,
    POKEMON,
    seconds_readable,
)


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
        log("yellow", f"Running Pokedaily")
        POKEMON.discord.post(DISCORD_POKEDAILY, "!pokedaily")

        if POKEMON.discord.data["user"] is None:
            POKEMON.discord.post(DISCORD_ALERTS, "Pokedaily, no user configured")
            log("green", f"Pokedaily, no user configured")
            return

        sleep(60 * 2)
        resp = POKEMON.discord.get(DISCORD_POKEDAILY_SEARCH.format(discord_id=POKEMON.discord.data["user"]))
        content = resp["messages"][0][0]["content"]
        message = parse_message(content)

        if message.repeat:
            log("red", f"Pokedaily not ready")
        else:
            POKEMON.discord.post(DISCORD_ALERTS, f"Pokedaily rewards ({message.rarity}):\n" + "\n".join(message.rewards))
            log("green", f"Pokedaily ({message.rarity}) rewards " + ", ".join(message.rewards))
