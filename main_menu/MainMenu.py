from datetime import datetime
from time import sleep
from tkinter import font as TKFont
import subprocess
import tkinter

from TwitchChannelPointsMiner.classes.chat.threads.DailyTasks import (
    battle_summary,
    check_finish_pokedex,
    stats_computer,
)

from .Utils import (
    clear_widgets,
    ok_alert,
    POKEMON,
    sync_all,
)
from .Settings import Settings
from .Missions import Missions


class MainMenu():
    def __init__(self, app):
        self.app = app
        self.app.title("Pokemon Comunity Game")
        self.app.resizable(False, False)
        font = TKFont.Font(size=15)
        self.button_conf = {
            "height": 2,
            "width": 13,
            "font": font
        }
        self.can_update = False

    def close(self):
        self.app.destroy()

    def page_main_menu(self):
        clear_widgets(self.app)
        self.app.geometry("400x425")
        f = tkinter.Frame(self.app)
        f2 = tkinter.Frame(self.app)
        padding = {
            "pady": 10,
            "padx": 10
        }
        update_state = "normal" if self.can_update else "disabled"
        tkinter.Button(f, text="Run PCG", command=self.run_pcg, **self.button_conf).grid(row=0, column=0, **padding)
        tkinter.Button(f, text="Update", command=self.run_update, state=update_state, **self.button_conf).grid(row=0, column=1, **padding)
        tkinter.Button(f, text="Missions", command=self.page_missions, **self.button_conf).grid(row=1, column=0, **padding)
        tkinter.Button(f, text="Settings", command=self.page_settings, **self.button_conf).grid(row=1, column=1, **padding)
        tkinter.Button(f, text="Spawn Stats", command=self.spawn_stats, **self.button_conf).grid(row=2, column=0, **padding)
        tkinter.Button(f, text="Bag Stats", command=self.bag_stats, **self.button_conf).grid(row=2, column=1, **padding)
        tkinter.Button(f, text="Battle Stats", command=self.battle_stats, **self.button_conf).grid(row=3, column=0, **padding)
        tkinter.Button(f, text="Pokedex Stats", command=self.pokedex_stats, **self.button_conf).grid(row=3, column=1, **padding)
        tkinter.Button(f2, text="Exit", command=self.close, **self.button_conf).grid(row=0, column=0, **padding)
        f.pack(anchor="center")
        f2.pack(anchor="center")

    def run(self):
        self.load()
        self.app.mainloop()

    @staticmethod
    def run_bat(filename):
        subprocess.Popen([filename])

    def spawn_stats(self):
        self.run_bat("run_stats.bat")

    def run_update(self):
        self.run_bat("update.bat")
        sleep(2)
        self.load()

    def run_pcg(self):
        self.run_bat("run_pcg.bat")

    def page_settings(self):
        Settings(self.app, self).run()

    def page_missions(self):
        Missions(self.app, self).run()

    def bag_stats(self):
        sync_all()
        msg = stats_computer(POKEMON, POKEMON.pokedex.stats)
        ok_alert(msg, "Bag Stats")

    def pokedex_stats(self):
        sync_all()
        msg = check_finish_pokedex(POKEMON, POKEMON.pokedex.stats)
        msg = msg.replace(":white_check_mark:", "✔")
        ok_alert(msg, "Pokedex Stats")

    def battle_stats(self):
        msg = battle_summary(datetime.now().date())
        ok_alert(msg, "Battle Stats")

    def load(self):
        self.check_updates()
        self.page_main_menu()

    def check_updates(self):
        subprocess.run(["git", "fetch"], stdout=subprocess.PIPE, text=True)
        git_status = subprocess.run(["git", "status"], stdout=subprocess.PIPE, text=True)
        self.can_update = "behind" in git_status.stdout


if __name__ == "__main__":
    app = tkinter.Tk()
    menu = MainMenu(app)
    menu.run()
