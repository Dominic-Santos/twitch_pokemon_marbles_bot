import tkinter
from tkinter import font as TKFont
import subprocess

from TwitchChannelPointsMiner.classes.entities.Pokemon.PokemonCG import PokemonComunityGame


def clear_widgets(app):
    for widget in app.winfo_children():
        widget.destroy()


class MainMenu():
    def __init__(self):
        self.app = tkinter.Tk()
        self.app.title("Pokemon Comunity Game")
        self.app.resizable(False, False)
        self.pcg = PokemonComunityGame()
        font = TKFont.Font(size=15)
        self.button_conf = {
            "height": 2,
            "width": 10,
            "font": font
        }

    def close(self):
        self.app.destroy()

    def page_main_menu(self):
        clear_widgets(self.app)
        self.app.geometry("350x250")
        f = tkinter.Frame(self.app)
        f2 = tkinter.Frame(self.app)
        padding = {
            "pady": 10,
            "padx": 10
        }
        tkinter.Button(f, text="Run PCG", command=self.run_pcg, **self.button_conf).grid(row=0, column=0, **padding)
        tkinter.Button(f, text="Update", command=self.run_update, **self.button_conf).grid(row=0, column=1, **padding)
        tkinter.Button(f, text="Stats", command=self.run_stats, **self.button_conf).grid(row=1, column=0, **padding)
        tkinter.Button(f, text="Settings", command=self.page_settings, **self.button_conf).grid(row=1, column=1, **padding)
        tkinter.Button(f2, text="Exit", command=self.close, **self.button_conf).grid(row=0, column=0, **padding)
        f.pack(anchor="center")
        f2.pack(anchor="center")

    def run(self):
        self.page_main_menu()
        self.app.mainloop()

    @staticmethod
    def run_bat(filename):
        subprocess.Popen([filename])

    def run_stats(self):
        self.run_bat("run_stats.bat")

    def run_update(self):
        self.run_bat("update.bat")

    def run_pcg(self):
        self.run_bat("run_pcg.bat")

    def page_settings(self):
        pass


if __name__ == "__main__":
    menu = MainMenu()
    menu.run()
