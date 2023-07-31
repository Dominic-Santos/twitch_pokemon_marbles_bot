import tkinter
from tkinter import font as TKFont
from tkinter.messagebox import showinfo
import subprocess

from TwitchChannelPointsMiner.classes.entities.Pokemon.PokemonCG import PokemonComunityGame

"""
    Settings Todo:
        Show hints button (?) -> Popup with hint? DONE
        Values:
            bool -> toggle True/False DONE
            int:
                if values exist:
                    values is list -> dropdown
                    values is dict -> dropdown from min to max
                else: any int
            str -> dropdown (no manual input so far) DONE
            list:
                values -> toggle (make list of all selected)
                no values -> list of items with order (do last not priority)
        Save / Load buttons
"""


def clear_widgets(app):
    for widget in app.winfo_children():
        widget.destroy()


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
        self.load()
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
        Settings(self.app, self).run()

    def load(self):
        self.page_main_menu()


class Settings():
    def __init__(self, app, parent):
        self.app = app
        self.parent = parent
        self.pcg = PokemonComunityGame()

        self.page = 0
        self.page_size = 10
        self.options = sorted(self.pcg.settings.keys())

    def run(self):
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
        tkinter.Button(f, text="Back", command=self.parent.load).grid(row=0, column=0, padx=3)
        tkinter.Button(f, text="<", command=self.prevPage, padx=10).grid(row=0, column=1, padx=3)
        self.pageLabel = tkinter.Label(f, text="")
        self.pageLabel.grid(row=0, column=2, padx=3)
        tkinter.Button(f, text=">", command=self.nextPage, padx=10).grid(row=0, column=3, padx=3)
        tkinter.Button(f, text="Save", command=self.save).grid(row=0, column=4, padx=3)
        f.pack(pady=10)

    def nextPage(self):
        if self.page < self.max_page:
            self.page += 1
        else:
            self.page = 0
        self.loadOptionsList()

    def prevPage(self):
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
            bg=self.getColor(self.pcg.settings[option]),
            text=self.getBoolText(self.pcg.settings[option])
        )

    @staticmethod
    def getBoolText(value):
        return "On" if value else "Off"

    @staticmethod
    def getColor(value):
        return "green" if value else "#f0f0f0"

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
        self.inputs = {}

        page = self.options[self.page_size * self.page: self.page_size * (self.page + 1)]

        for i, option_name in enumerate(page):
            option_value = self.pcg.settings[option_name]
            option_settings = self.pcg.default_settings[option_name]
            option_type = type(option_value)

            tkinter.Label(self.list_frame, text=option_name).grid(row=i, column=0, pady=3, padx=5)

            val = tkinter.Button(self.list_frame, text="<tmp>", padx=5, command=self.doNothing)

            if option_type == bool:
                val = tkinter.Button(self.list_frame, text=self.getBoolText(option_value), padx=5, bg=self.getColor(option_value))
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

            val.grid(row=i, column=1, pady=3, padx=5)

            tkinter.Button(
                self.list_frame,
                text="?",
                padx=5,
                command=(lambda title=option_name, text=option_settings["hint"]: self.showHint(title, text))
            ).grid(row=i, column=2, pady=3, padx=5)

        self.refreshPageLabel()

    def doNothing(self):
        pass

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


if __name__ == "__main__":
    app = tkinter.Tk()
    menu = MainMenu(app)
    menu.run()
