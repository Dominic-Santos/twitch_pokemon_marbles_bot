from tkinter import font as TKFont
import tkinter

from .Utils import (
    clear_widgets,
    get_image,
    get_sprite_cached,
    getBoolText,
    getColor,
    POKEMON,
    POKEMON_API,
)


class Missions():
    def __init__(self, app, parent):
        self.app = app
        self.parent = parent
        self.page = 0
        self.page_size = 5
        self.mode = "all"

        self.loadMissions()
        self.filterOptions()

    def filterOptions(self):
        if self.mode == "all":
            options = self.missions
        elif self.mode == "complete":
            options = [mission for mission in self.missions if mission["goal"] <= mission["progress"]]
        elif self.mode == "incomplete":
            options = [mission for mission in self.missions if mission["goal"] > mission["progress"]]
        elif self.mode == "on":
            options = [mission for mission in self.missions if POKEMON.missions.get_unique_id(mission) not in POKEMON.settings["skip_missions"]]
        elif self.mode == "off":
            options = [mission for mission in self.missions if POKEMON.missions.get_unique_id(mission) in POKEMON.settings["skip_missions"]]
        self.options = sorted(options, key=lambda x: x["name"])
        self.max_page = (len(self.options) // self.page_size) - 1 + (1 if len(self.options) % self.page_size != 0 else 0)

    def loadMissions(self):
        missions = POKEMON_API.get_missions()
        POKEMON.sync_missions(missions)
        self.missions = missions["missions"]

        mission_names = [POKEMON.missions.get_unique_id(mission) for mission in self.missions]
        POKEMON.settings["skip_missions"] = [x for x in POKEMON.settings["skip_missions"] if x in mission_names]

        for mission in self.missions:
            if mission["rewardPokemon"] is not None:
                get_sprite_cached("pokemon", str(mission["rewardPokemon"]["id"]))
            else:
                get_sprite_cached(mission["rewardItem"]["category"], mission["rewardItem"]["sprite_name"])

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

    def filterButton(self, mode):
        if self.mode == mode:
            self.mode = "all"
        else:
            self.mode = mode
        self.page = 0
        self.filterOptions()
        self.loadOptionsList()
        self.completeBtn.config(bg=getColor(self.mode == "complete"))
        self.incompleteBtn.config(bg=getColor(self.mode == "incomplete"))
        self.onBtn.config(bg=getColor(self.mode == "on"))
        self.offBtn.config(bg=getColor(self.mode == "off"))

    def createFrame(self):
        f = tkinter.Frame(self.app)
        self.completeBtn = tkinter.Button(f, text="Complete", command=lambda: self.filterButton("complete"), padx=5)
        self.completeBtn.grid(row=0, column=0, padx=3)
        self.incompleteBtn = tkinter.Button(f, text="Incomplete", command=lambda: self.filterButton("incomplete"), padx=5)
        self.incompleteBtn.grid(row=0, column=1, padx=3)
        self.onBtn = tkinter.Button(f, text="On", command=lambda: self.filterButton("on"), padx=5)
        self.onBtn.grid(row=0, column=2, padx=3)
        self.offBtn = tkinter.Button(f, text="Off", command=lambda: self.filterButton("off"), padx=5)
        self.offBtn.grid(row=0, column=3, padx=3)
        f.pack(pady=10)

        self.list_frame = tkinter.Frame(self.app)
        self.list_frame.pack(pady=10, padx=10)

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

    def loadOptionsList(self):
        clear_widgets(self.list_frame)
        font = TKFont.Font(size=12)

        page = self.options[self.page_size * self.page: self.page_size * (self.page + 1)]

        for i, mission in enumerate(page):
            mission_name = POKEMON.missions.get_unique_id(mission)
            mission_complete = mission["goal"] <= mission["progress"]
            do_mission = mission_name not in POKEMON.settings["skip_missions"]

            if mission["rewardPokemon"] is not None:
                img_path = get_sprite_cached("pokemon", str(mission["rewardPokemon"]["id"]))
                reward = mission["rewardPokemon"]["name"]

            else:
                img_path = get_sprite_cached(mission["rewardItem"]["category"], mission["rewardItem"]["sprite_name"])
                reward = str(mission["rewardItem"]["amount"]) + "x " + mission["rewardItem"]["name"]

            reward_frame = tkinter.Frame(self.list_frame)
            canvas = tkinter.Canvas(reward_frame, width=96, height=96)
            try:
                tkimg = get_image(img_path)
                # tkimg = tkinter.PhotoImage(file=img_path)
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
        if option in POKEMON.settings["skip_missions"]:
            POKEMON.settings["skip_missions"].remove(option)
            do_mission = True
        else:
            POKEMON.settings["skip_missions"].append(option)
            do_mission = False

        btn.config(
            bg=getColor(do_mission),
            text=getBoolText(do_mission)
        )

    def refreshPageLabel(self):
        self.pageLabel.config(text=f"Page: {min(self.page + 1, self.max_page + 1)}/{self.max_page + 1}")
