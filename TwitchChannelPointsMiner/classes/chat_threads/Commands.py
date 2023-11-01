from time import sleep
from datetime import datetime
import traceback

from ..ChatLogs import log
from ..ChatUtils import (
    DISCORD_COMMANDS_SEARCH,
    DISCORD_DELETE_COMMAND,
    POKEMON,
)


class Commands(object):
    def commands_timer(self):
        thread_name = "Commands Timer"
        wait = 60  # 1 min
        log("yellow", f"Thread Created - {thread_name}")

        running = True

        while running:
            try:
                self.commands()
            except KeyboardInterrupt:
                running = False
            except Exception as ex:
                str_ex = str(ex)
                log("red", f"{thread_name} Error - {str_ex}")
                print(traceback.format_exc())
            sleep(wait)

        log("yellow", f"Thread Closing - {thread_name}")

    def run_command(self, command):
        log("yellow", f"Running Command - {command}")
        cur_date = datetime.now().date()
        if command == "computer":
            self.stats_computer()
        elif command == "battles":
            self.battle_summary(cur_date)
        elif command == "pokedex":
            self.show_pokedex()
        elif command in ["finish pokedex", "finish"]:
            self.check_finish_pokedex()
        elif command in ["catch", "catch rates"]:
            self.catch_rates(cur_date)
        elif command == "loyalty":
            self.check_loyalty()

    def commands(self):
        resp = POKEMON.discord.get(DISCORD_COMMANDS_SEARCH.format(discord_id=POKEMON.discord.data["user"]))

        if len(resp["messages"]) == 0:
            return

        latest_message = resp["messages"][0][0]

        POKEMON.discord.delete(DISCORD_DELETE_COMMAND.format(message_id=latest_message["id"]))

        command = latest_message["content"].replace("_", " ").strip().lower()

        self.run_command(command)
