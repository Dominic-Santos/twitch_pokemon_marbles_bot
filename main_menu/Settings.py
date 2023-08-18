import tkinter
from tkinter.messagebox import showinfo

from .Classes import DropDownValue, MultiSelect
from .Utils import (
    clear_widgets,
    getBoolText,
    getColor,
    POKEMON,
)


class Settings():
    def __init__(self, app, parent):
        self.app = app
        self.parent = parent

        self.skip_options = ["skip_missions"]
        self.options = sorted(k for k in POKEMON.settings.keys() if k not in self.skip_options)

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
        POKEMON.save_settings()
        self.parent.load()

    def back(self):
        POKEMON.load_settings()
        self.parent.load()

    def createFrame(self):
        self.list_frame = tkinter.Frame(self.app)
        self.list_frame.pack(pady=10, padx=10)

        self.max_page = (len(self.options) // self.page_size) - 1 + (1 if len(self.options) % self.page_size != 0 else 0)

        f = tkinter.Frame(self.app)
        tkinter.Button(f, text="Back", command=self.back, padx=5).grid(row=0, column=0, padx=3)
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
        POKEMON.settings[option] = not POKEMON.settings[option]
        btn.config(
            bg=getColor(POKEMON.settings[option]),
            text=getBoolText(POKEMON.settings[option])
        )

    def changeDropdown(self, option, dropdown):
        if isinstance(POKEMON.settings[option], int):
            POKEMON.settings[option] = int(dropdown.get())
        else:
            POKEMON.settings[option] = dropdown.get()

    def changeIntEntry(self, option, entry, inp):
        val = entry.get()
        if val.isnumeric():
            inp.config(bg="white")
            POKEMON.settings[option] = int(val)
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
                option_value = POKEMON.settings[option_name]
                option_settings = POKEMON.default_settings[option_name]
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
        ms = MultiSelect(self.app, self, option, POKEMON.default_settings[option]["values"], POKEMON.settings[option])
        ms.run()

    def multiSelectCallback(self, option, value):
        POKEMON.settings[option] = value
        self.load()

    def refreshPageLabel(self):
        self.pageLabel.config(text=f"Page: {min(self.page + 1, self.max_page + 1)}/{self.max_page + 1}")
