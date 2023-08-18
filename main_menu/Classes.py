import tkinter

from .Utils import (
    clear_widgets,
    getBoolText,
    getColor,
)


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
