import json
import tkinter
from tkinter import font as TKFont
from tkinter.messagebox import showinfo
import subprocess
from time import sleep

from TwitchChannelPointsMiner.classes.entities.Pokemon.PokemonCG import PokemonComunityGame
from TwitchChannelPointsMiner.classes.entities.Pokemon.Utils import get_sprite


def clear_widgets(app):
    for widget in app.winfo_children():
        widget.destroy()


def getBoolText(value):
    return "On" if value else "Off"


def getColor(value):
    return "green" if value else "#f0f0f0"


class MainMenu():
    def __init__(self, app):
        self.app = app
        self.app.title("Pokemon Comunity Game")
        self.app.resizable(False, False)
        font = TKFont.Font(size=15)
        self.button_conf = {
            "height": 2,
            "width": 10,
            "font": font
        }
        self.can_update = False

    def close(self):
        self.app.destroy()

    def page_main_menu(self):
        clear_widgets(self.app)
        self.app.geometry("350x350")
        f = tkinter.Frame(self.app)
        f2 = tkinter.Frame(self.app)
        padding = {
            "pady": 10,
            "padx": 10
        }
        update_state = "normal" if self.can_update else "disabled"
        tkinter.Button(f, text="Run PCG", command=self.run_pcg, **self.button_conf).grid(row=0, column=0, **padding)
        tkinter.Button(f, text="Update", command=self.run_update, state=update_state, **self.button_conf).grid(row=0, column=1, **padding)
        tkinter.Button(f, text="Stats", command=self.run_stats, **self.button_conf).grid(row=1, column=0, **padding)
        tkinter.Button(f, text="Settings", command=self.page_settings, **self.button_conf).grid(row=1, column=1, **padding)
        tkinter.Button(f, text="Missions", command=self.page_missions, **self.button_conf).grid(row=2, column=0, **padding)
        tkinter.Button(f2, text="Exit", command=self.close, **self.button_conf).grid(row=0, column=0, **padding)
        f.pack(anchor="center")
        f2.pack(anchor="center")

    def run(self):
        self.load()
        self.app.mainloop()

    @staticmethod
    def run_bat(filename):
        subprocess.Popen([filename])

    def run_stats(self):
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

    def load(self):
        self.check_updates()
        self.page_main_menu()

    def check_updates(self):
        git_status = subprocess.run(["git", "status"], stdout=subprocess.PIPE, text=True)
        self.can_update = "behind" in git_status.stdout


class Settings():
    def __init__(self, app, parent):
        self.app = app
        self.parent = parent
        self.pcg = PokemonComunityGame()
        self.skip_options = ["skip_missions"]
        self.options = sorted(k for k in self.pcg.settings.keys() if k not in self.skip_options)

        self.page = 0
        self.page_size = 20
        self.columns = 2

    def run(self):
        self.load()

    def load(self):
        clear_widgets(self.app)
        self.createFrame()
        self.loadOptionsList()
        self.app.geometry("")

    def save(self):
        self.pcg.save_settings()
        self.parent.load()

    def createFrame(self):
        self.list_frame = tkinter.Frame(self.app)
        self.list_frame.pack(pady=10, padx=10)

        self.max_page = (len(self.options) // self.page_size) - 1 + (1 if len(self.options) % self.page_size != 0 else 0)

        f = tkinter.Frame(self.app)
        tkinter.Button(f, text="Back", command=self.parent.load, padx=5).grid(row=0, column=0, padx=3)
        tkinter.Button(f, text="<", command=self.prevPage, padx=10).grid(row=0, column=1, padx=3)
        self.pageLabel = tkinter.Label(f, text="")
        self.pageLabel.grid(row=0, column=2, padx=3)
        tkinter.Button(f, text=">", command=self.nextPage, padx=10).grid(row=0, column=3, padx=3)
        tkinter.Button(f, text="Save", command=self.save, padx=5).grid(row=0, column=4, padx=3)
        f.pack(pady=10)

    def nextPage(self):
        if self.max_page == 0:
            return
        if self.page < self.max_page:
            self.page += 1
        else:
            self.page = 0
        self.loadOptionsList()

    def prevPage(self):
        if self.max_page == 0:
            return
        if self.page > 0:
            self.page -= 1
        else:
            self.page = self.max_page
        self.loadOptionsList()

    def showHint(self, title, text):
        showinfo(title, text)

    def toggleBool(self, option, btn):
        self.pcg.settings[option] = not self.pcg.settings[option]
        btn.config(
            bg=getColor(self.pcg.settings[option]),
            text=getBoolText(self.pcg.settings[option])
        )

    def changeDropdown(self, option, dropdown):
        if isinstance(self.pcg.settings[option], int):
            self.pcg.settings[option] = int(dropdown.get())
        else:
            self.pcg.settings[option] = dropdown.get()

    def changeIntEntry(self, option, entry, inp):
        val = entry.get()
        if val.isnumeric():
            inp.config(bg="white")
            self.pcg.settings[option] = int(val)
            if str(int(val)) != val:
                entry.set(int(val))
        else:
            inp.config(bg="red")

    def loadOptionsList(self):
        clear_widgets(self.list_frame)

        pages = self.options[self.page_size * self.page: self.page_size * (self.page + 1)]

        page_nrs = []
        for i in range(self.columns):
            if len(pages) > self.page_size / self.columns * i:
                page_nrs.append(i)

        for page_nr in page_nrs:
            page = pages[int(self.page_size / self.columns * page_nr): int(self.page_size / self.columns * page_nr + self.page_size / self.columns)]

            # page = self.options[self.page_size * self.page: self.page_size * (self.page + 1)]

            for i, option_name in enumerate(page):
                option_value = self.pcg.settings[option_name]
                option_settings = self.pcg.default_settings[option_name]
                option_type = type(option_value)
                offset = 3 * page_nr

                tkinter.Label(self.list_frame, text=option_name).grid(row=i, column=0 + offset, pady=3, padx=5)

                val = tkinter.Label(self.list_frame, text="<not finished>", padx=5)

                if option_type == bool:
                    val = tkinter.Button(self.list_frame, text=getBoolText(option_value), padx=5, bg=getColor(option_value))
                    val.config(command=(lambda option=option_name, btn=val: self.toggleBool(option, btn)))
                elif option_type == str:
                    dd = DropDownValue(option_name, option_value, self.changeDropdown)
                    val = tkinter.OptionMenu(self.list_frame, dd, *option_settings["values"])
                    dd.set_dropdown(val)
                elif option_type == int:
                    if "values" in option_settings:
                        dd = DropDownValue(option_name, option_value, self.changeDropdown)
                        val = tkinter.OptionMenu(self.list_frame, dd, *list(range(option_settings["values"]["min"], option_settings["values"]["max"] + 1)))
                        dd.set_dropdown(val)
                    else:
                        var = tkinter.StringVar()
                        var.set(option_value)
                        val = tkinter.Entry(
                            self.list_frame,
                            textvariable=var,
                        )
                        var.trace("w", (lambda _, __, ___, option=option_name, value=var, inp=val: self.changeIntEntry(option, value, inp)))
                elif option_type == list:
                    if "values" in option_settings:
                        val = tkinter.Button(
                            self.list_frame,
                            text=str(len(option_value)) + " Selected",
                            padx=5,
                            command=(lambda option=option_name: self.openMultiSelect(option))
                        )
                    else:
                        val = tkinter.Label(self.list_frame, text=str(len(option_value)) + " Items", padx=5)

                if val is not None:
                    val.grid(row=i, column=1 + offset, pady=3, padx=5)

                tkinter.Button(
                    self.list_frame,
                    text="?",
                    padx=5,
                    command=(lambda title=option_name, text=option_settings["hint"]: self.showHint(title, text))
                ).grid(row=i, column=2 + offset, pady=3, padx=5)

        self.refreshPageLabel()

    def openMultiSelect(self, option):
        ms = MultiSelect(self.app, self, option, self.pcg.default_settings[option]["values"], self.pcg.settings[option])
        ms.run()

    def multiSelectCallback(self, option, value):
        self.pcg.settings[option] = value
        self.load()

    def refreshPageLabel(self):
        self.pageLabel.config(text=f"Page: {min(self.page + 1, self.max_page + 1)}/{self.max_page + 1}")


class Missions():
    def __init__(self, app, parent):
        self.app = app
        self.parent = parent
        self.pcg = PokemonComunityGame()
        try:
            with open("results/API/get_missions.json") as f:
                self.options = json.load(f)["missions"]
        except Exception as e:
            print(e)
            self.options = []

        mission_names = [self.pcg.missions.get_unique_id(mission) for mission in self.options]
        self.pcg.settings["skip_missions"] = [x for x in self.pcg.settings["skip_missions"] if x in mission_names]

        self.options = sorted(self.options, key=lambda x: x["name"])

        self.page = 0
        self.page_size = 5

    def run(self):
        self.load()

    def load(self):
        clear_widgets(self.app)
        self.createFrame()
        self.loadOptionsList()
        self.app.geometry("")

    def save(self):
        self.pcg.save_settings()
        self.parent.load()

    def createFrame(self):
        self.list_frame = tkinter.Frame(self.app)
        self.list_frame.pack(pady=10, padx=10)

        self.max_page = (len(self.options) // self.page_size) - 1 + (1 if len(self.options) % self.page_size != 0 else 0)

        f = tkinter.Frame(self.app)
        tkinter.Button(f, text="Back", command=self.parent.load, padx=5).grid(row=0, column=0, padx=3)
        tkinter.Button(f, text="<", command=self.prevPage, padx=10).grid(row=0, column=1, padx=3)
        self.pageLabel = tkinter.Label(f, text="")
        self.pageLabel.grid(row=0, column=2, padx=3)
        tkinter.Button(f, text=">", command=self.nextPage, padx=10).grid(row=0, column=3, padx=3)
        tkinter.Button(f, text="Save", command=self.save, padx=5).grid(row=0, column=4, padx=3)
        f.pack(pady=10)

    def nextPage(self):
        if self.max_page == 0:
            return
        if self.page < self.max_page:
            self.page += 1
        else:
            self.page = 0
        self.loadOptionsList()

    def prevPage(self):
        if self.max_page == 0:
            return
        if self.page > 0:
            self.page -= 1
        else:
            self.page = self.max_page
        self.loadOptionsList()

    def loadOptionsList(self):
        clear_widgets(self.list_frame)
        font = TKFont.Font(size=12)

        page = self.options[self.page_size * self.page: self.page_size * (self.page + 1)]

        for i, mission in enumerate(page):
            mission_name = self.pcg.missions.get_unique_id(mission)
            mission_complete = mission["goal"] <= mission["progress"]
            do_mission = mission_name not in self.pcg.settings["skip_missions"]

            if mission["rewardPokemon"] is not None:
                img_path = get_sprite("pokemon", str(mission["rewardPokemon"]["id"]), battle=True, path=True)
                reward = mission["rewardPokemon"]["name"]

            else:
                img_path = get_sprite(mission["rewardItem"]["category"], mission["rewardItem"]["sprite_name"], path=True)
                reward = str(mission["rewardItem"]["amount"]) + "x " + mission["rewardItem"]["name"]

            reward_frame = tkinter.Frame(self.list_frame)
            canvas = tkinter.Canvas(reward_frame, width=96, height=96)
            try:
                tkimg = tkinter.PhotoImage(file=img_path)
                canvas.image = tkimg
                canvas.create_image(96 / 2, 96 / 2, image=tkimg)
            except Exception as e:
                print(e)

            canvas.grid(row=0, column=0)
            tkinter.Label(reward_frame, font=font, text=reward).grid(row=1, column=0)

            tkinter.Label(self.list_frame, text=mission["name"], font=font).grid(row=i, column=0, pady=3, padx=5)
            tkinter.Label(self.list_frame, text=f"{mission['progress']}/{mission['goal']}", padx=10, pady=10, font=font, bg=getColor(mission_complete)).grid(row=i, column=1, pady=3, padx=5)

            reward_frame.grid(row=i, column=2, pady=3, padx=5)

            val = tkinter.Button(self.list_frame, text=getBoolText(do_mission), padx=10, pady=5, font=font, bg=getColor(do_mission))
            val.config(command=(lambda option=mission_name, btn=val: self.toggleBool(option, btn)))
            val.grid(row=i, column=3, pady=3, padx=5)

        self.refreshPageLabel()

    def toggleBool(self, option, btn):
        if option in self.pcg.settings["skip_missions"]:
            self.pcg.settings["skip_missions"].remove(option)
            do_mission = True
        else:
            self.pcg.settings["skip_missions"].append(option)
            do_mission = False

        btn.config(
            bg=getColor(do_mission),
            text=getBoolText(do_mission)
        )

    def refreshPageLabel(self):
        self.pageLabel.config(text=f"Page: {min(self.page + 1, self.max_page + 1)}/{self.max_page + 1}")


class DropDownValue(tkinter.StringVar):
    def __init__(self, option, value, command):
        self.command = command
        self.option = option
        super().__init__()
        super().set(value)

    def set(self, value):
        super().set(value)
        self.command(self.option, self)

    def set_dropdown(self, dropdown):
        self.dropdown = dropdown


class MultiSelect():
    def __init__(self, app, parent, option, options, selected):
        self.app = app
        self.parent = parent
        self.option = option
        self.options = sorted(options)
        self.selected = selected

        self.page = 0
        self.page_size = 40
        self.columns = 4

    def run(self):
        self.load()

    def load(self):
        clear_widgets(self.app)
        self.createFrame()
        self.loadOptionsList()
        self.app.geometry("")

    def save(self):
        self.parent.multiSelectCallback(self.option, self.selected)

    def createFrame(self):
        self.list_frame = tkinter.Frame(self.app)
        self.list_frame.pack(pady=10, padx=10)

        self.max_page = (len(self.options) // self.page_size) - 1 + (1 if len(self.options) % self.page_size != 0 else 0)

        f = tkinter.Frame(self.app)
        tkinter.Button(f, text="Back", command=self.parent.load, padx=5).grid(row=0, column=0, padx=3)
        tkinter.Button(f, text="<", command=self.prevPage, padx=10).grid(row=0, column=1, padx=3)
        self.pageLabel = tkinter.Label(f, text="")
        self.pageLabel.grid(row=0, column=2, padx=3)
        tkinter.Button(f, text=">", command=self.nextPage, padx=10).grid(row=0, column=3, padx=3)
        tkinter.Button(f, text="Save", command=self.save, padx=5).grid(row=0, column=4, padx=3)
        f.pack(pady=10)

    def nextPage(self):
        if self.max_page == 0:
            return
        if self.page < self.max_page:
            self.page += 1
        else:
            self.page = 0
        self.loadOptionsList()

    def prevPage(self):
        if self.max_page == 0:
            return
        if self.page > 0:
            self.page -= 1
        else:
            self.page = self.max_page
        self.loadOptionsList()

    def toggleBool(self, option, btn):
        if option in self.selected:
            self.selected.remove(option)
        else:
            self.selected.append(option)

        btn.config(
            bg=getColor(option in self.selected),
            text=getBoolText(option in self.selected)
        )

    def loadOptionsList(self):
        clear_widgets(self.list_frame)

        pages = self.options[self.page_size * self.page: self.page_size * (self.page + 1)]

        page_nrs = []
        for i in range(self.columns):
            if len(pages) > self.page_size / self.columns * i:
                page_nrs.append(i)

        for page_nr in page_nrs:
            page = pages[int(self.page_size / self.columns * page_nr): int(self.page_size / self.columns * page_nr + self.page_size / self.columns)]
            for i, option_name in enumerate(page):
                option_value = option_name in self.selected
                offset = 2 * page_nr

                tkinter.Label(self.list_frame, text=option_name).grid(row=i, column=0 + offset, pady=3, padx=5)

                val = tkinter.Button(self.list_frame, text=getBoolText(option_value), padx=5, bg=getColor(option_value))
                val.config(command=(lambda option=option_name, btn=val: self.toggleBool(option, btn)))
                val.grid(row=i, column=1 + offset, pady=3, padx=5)

        self.refreshPageLabel()

    def refreshPageLabel(self):
        self.pageLabel.config(text=f"Page: {min(self.page + 1, self.max_page + 1)}/{self.max_page + 1}")


if __name__ == "__main__":
    app = tkinter.Tk()
    menu = MainMenu(app)
    menu.run()
