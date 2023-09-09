from time import sleep

from .ChatUtils import THREADCONTROLLER, create_thread, POKEMON
from .ChatLogs import log
from .chat_threads.DailyTasks import DailyTasks
from .chat_threads.Pokedaily import Pokedaily
from .chat_threads.PokemonSpawn import PokemonSpawn
from .chat_threads.Wondertrade import Wondertrade
from .chat_threads.AutoBattle import AutoBattle


class ChatThreads(DailyTasks, Pokedaily, PokemonSpawn, Wondertrade, AutoBattle):
    def start_threads(self):
        if THREADCONTROLLER.started is False:
            THREADCONTROLLER.started = True
            log("yellow", f"Threads Starting")
            create_thread(self.spawn_timer)
            create_thread(self.settings_reloader)
            create_thread(self.wondertrade_timer)
            create_thread(self.pokedaily_timer)
            create_thread(self.daily_task_timer)
            create_thread(self.battle_timer)

    def settings_reloader(self):
        thread_name = "Settings Reloader"
        log("yellow", f"Thread Created - {thread_name}")

        running = True
        while running:
            sleep(60)
            try:
                changes = POKEMON.load_settings()
                if changes:
                    log("green", "Settings Reloaded")
            except KeyboardInterrupt:
                running = False
            except Exception as ex:
                log("red", f"{thread_name} Error - " + str(ex))
        log("yellow", f"Thread Closing - {thread_name}")
