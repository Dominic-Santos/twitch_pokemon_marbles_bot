import random
from datetime import datetime
import json

from .Discord import Discord
from .Missions import Missions
from .Inventory import Inventory, POKEMON_TYPES
from .Pokedex import Pokedex
from .Computer import Computer
from .Loyalty import Loyalty

SETTINGS_FILE = "pokemon.json"
TIERS = ["S", "A", "B", "C"]


class PokemonComunityGame(Loyalty):
    def __init__(self):
        Loyalty.__init__(self)

        self.delay = 0
        self.reset_timer()
        self.last_random = None
        self.alerts = False
        self.alerts_channel = ""

        self.channel_list = []
        self.online_channels = []

        self.discord = Discord()
        self.inventory = Inventory()
        self.pokedex = Pokedex()
        self.missions = Missions()
        self.missions.new_missions_callback = self.new_missions
        self.computer = Computer()

        all_pokemon = [self.pokedex.clean_name(self.pokedex.stats(str(x)).name) for x in range(1, self.pokedex.total + 1)]

        self.default_settings = {
            "alert_new_missions": {
                "value": False,
                "hint": "Send alert to discord when new missions detected",
            },
            "catch_everything": {
                "value": False,
                "hint": "Catch every pokemon that spawns",
            },
            "catch_alternates": {
                "value": False,
                "hint": "Try to complete the alt pokedex",
            },
            "catch_fish": {
                "value": False,
                "hint": "Catch all Fish pokemon (used for events)",
            },
            "trade_tiers": {
                "value": ["A", "B", "C"],
                "hint": "Wondertrade any pokemon of the selected tiers",
                "values": TIERS,
            },
            "catch_dogs": {
                "value": False,
                "hint": "Catch all Dog pokemon (used for events)",
            },
            "catch_cats": {
                "value": False,
                "hint": "Catch all Cat pokemon (used for events)",
            },
            "complete_bag": {
                "value": False,
                "hint": "Collect one of each pokemon in bag, including alt versions (even if not in alt pokedex)",
            },
            "use_special_balls": {
                "value": True,
                "hint": "Use all balls, not just Poke, Great, Ultra and Premier",
            },
            "catch_starters": {
                "value": True,
                "hint": "Catch all Starter pokemon",
            },
            "catch_legendaries": {
                "value": True,
                "hint": "Catch all Legendary pokemon",
            },
            "auto_battle": {
                "value": False,
                "hint": "Allow AI to battle hard stadium battles",
            },
            "battle_heal": {
                "value": False,
                "hint": "Heal Pokemon in battle team",
            },
            "battle_heal_percent": {
                "value": 50,
                "hint": "Heal pokemon when below a certain HP percent",
                "values": {
                    "max": 99,
                    "min": 0,
                },
            },
            "auto_battle_challenge": {
                "value": True,
                "hint": "When auto_battle is active, also allow AI to attempt Challenges when available",
            },
            "money_saving": {
                "value": 0,
                "hint": "When cash is bellow this amount, save Ultraballs for A tiers and Greatballs for B tiers",
            },
            "spend_money_above": {
                "value": 0,
                "hint": "When cash is above this amount, catch any pokemon that spawns, set to 0 to disable",
            },
            "spend_money_strategy": {
                "value": "save",
                "hint": "When spend_money_above is active, chose what catch strategy to apply:\n -best ball available\n -worst ball available\n -save Ultraballs for A tiers and Greatballs for B tiers",
                "values": ["save", "best", "worst"],
            },
            "spend_money_level": {
                "value": 0,
                "hint": "Only spend money when a streamer above this level is online:\n  2 = featured\n  1 = Deemonrider/Jonaswagern\n  0 = all",
                "values": {
                    "max": 2,
                    "min": 0,
                },
            },
            "catch": {
                "value": [],
                "hint": "Catch any of the selected pokemon",
                "values": all_pokemon,
            },
            "shiny_hunt": {
                "value": [],
                "hint": "Catch any of the selected pokemon with cherish balls if possible",
                "values": all_pokemon,
            },
            "catch_tiers": {
                "value": [],
                "hint": "Catch any pokemon of the selected tiers",
                "values": TIERS,
            },
            "catch_types": {
                "value": [],
                "hint": "Catch any pokemon of the selected types",
                "values": POKEMON_TYPES,
            },
            "catch_stones": {
                "value": [],
                "hint": "Catch any pokemon of the selected types with Stone balls",
                "values": POKEMON_TYPES,
            },
            "channel_priority": {
                "value": [],
                "hint": "Priority channels in order of most important to least",
            },
            "trade_legendaries": {
                "value": False,
                "hint": "Trade duplicate legendaries",
            },
            "trade_starters": {
                "value": False,
                "hint": "Trade duplicate starters",
            },
            "trade_keep": {
                "value": [],
                "hint": "Won't wondertrade any of the selected pokemon",
                "values": all_pokemon,
            },
            "skip_missions": {
                # requires special way to toggle each mission
                "value": [],
                "hint": "Skip missions selected missions",
            },
            "skip_missions_default": {
                "value": False,
                "hint": "Skip new missions by default",
            }
        }

        self.settings = {key: self.default_settings[key]["value"] for key in self.default_settings}

        self.load_settings()
        self.load_discord_settings()

        self.discord.connect()

    def reset_timer(self):
        self.catch_timer = datetime.utcnow()

    def save_settings(self):
        with open(SETTINGS_FILE, "w") as f:
            to_write = {
                "settings": self.settings,
                "discord": self.discord.data
            }
            f.write(json.dumps(to_write, indent=4))

    def load_settings(self):
        with open(SETTINGS_FILE, "r") as f:
            j = json.load(f)
            changes = self.set(j.get("settings", {}))

        self.inventory.use_special_balls = self.settings["use_special_balls"]
        self.inventory.spend_money_strategy = self.settings["spend_money_strategy"]
        self.inventory.money_saving = self.settings["money_saving"]
        self.missions.skip = self.settings["skip_missions"]
        self.missions.skip_default = self.settings["skip_missions_default"]

        return changes

    def load_discord_settings(self):
        with open(SETTINGS_FILE, "r") as f:
            j = json.load(f)
            self.discord.set(j.get("discord", {}))

    def set(self, settings):
        changes = False
        for k in settings:
            if k in self.settings:
                if self.settings[k] != settings[k]:
                    self.settings[k] = settings[k]
                    changes = True
        return changes

    def check_catch(self):
        if (datetime.utcnow() - self.catch_timer).total_seconds() > self.delay:
            return True

        return False

    def sync_inventory(self, inv):
        self.inventory.set(inv)

    def sync_pokedex(self, dex):
        self.pokedex.set(dex)
        self.computer.total = self.pokedex.total

    def sync_computer(self, all_pokemon):
        self.computer.set(all_pokemon)

    def sync_missions(self, missions):
        self.missions.set(missions)

    def set_alerts(self, alerts, discord_alerts_channel=""):
        self.alerts_channel = discord_alerts_channel
        self.alerts = alerts

    def new_missions(self, new_missions):
        self.save_settings()
        if self.alerts and self.settings["alert_new_missions"]:
            mission_strings = []
            for mission in new_missions:
                reward = self.missions.get_reward(mission)
                mission_strings.append(f"{mission['name']} ({mission['goal']}) - {reward['reward']}")

            msg = "New Missions:\n    " + "\n    ".join(mission_strings)
            self.discord.post(self.alerts_channel, msg)

    def set_delay(self, delay):
        self.delay = delay

    def need_pokemon(self, pokemon):
        reasons = []

        if self.pokedex.need(pokemon):
            reasons.append("pokedex")

        if self.settings["complete_bag"]:
            if self.computer.need(pokemon):
                reasons.append("bag")

        if self.settings["catch_alternates"]:
            if pokemon.pokedex_id > self.pokedex.total:
                if self.pokedex.need_alt(pokemon):
                    reasons.append("alt")

        missions = self.missions.check_all_missions(pokemon)
        for mission in missions:
            reasons.append(mission)

        if self.pokedex.clean_name(pokemon) in self.settings["catch"]:
            reasons.append("catch")

        elif self.pokedex.clean_name(pokemon) in self.settings["shiny_hunt"]:
            reasons.append("shiny_hunt")

        for poke_type in pokemon.types:
            if poke_type in self.settings["catch_types"]:
                reasons.append(f"all_type ({poke_type.title()})")

        for poke_type in pokemon.types:
            if poke_type in self.settings["catch_stones"]:
                reasons.append(f"stones ({poke_type.title()})")

        if self.settings["catch_legendaries"] and self.pokedex.legendary(pokemon):
            reasons.append("legendary")

        if self.settings["catch_starters"] and self.pokedex.starter(pokemon):
            reasons.append("starter")

        if pokemon.tier in self.settings["catch_tiers"]:
            reasons.append("tiers")

        if self.settings["catch_fish"] and pokemon.is_fish:
            reasons.append("all_fish")

        if self.settings["catch_dogs"] and pokemon.is_dog:
            reasons.append("all_dogs")

        if self.settings["catch_cats"] and pokemon.is_cat:
            reasons.append("all_cats")

        if self.settings["catch_everything"]:
            # catch anything:
            reasons.append("everything")

        if self.settings["spend_money_above"] > 0 and self.settings["spend_money_above"] < self.inventory.cash:
            # Catch anything if money above X, X <= 0 is ignored
            channel = self.get_channel()
            if channel is not None:
                if channel not in self.loyalty_data or self.loyalty_data[channel]["featured"] >= self.settings["spend_money_level"]:
                    reasons.append("spend_money")
        return reasons

    # ########### Channels ############

    def add_channel(self, channel):
        if channel not in self.channel_list:
            self.channel_list.append(channel)

    def remove_channel(self, channel):
        if channel in self.channel_list:
            self.channel_list.remove(channel)

    def channel_online(self, channel):
        if channel not in self.online_channels:
            self.online_channels.append(channel)

    def channel_offline(self, channel):
        if channel in self.online_channels:
            self.online_channels.remove(channel)

    def get_channel(self, ignore_priority=False):
        if len(self.channel_list) == 0:
            return None

        if not ignore_priority:
            for channel in self.settings["channel_priority"]:
                if channel in self.online_channels:
                    return channel

        return self.get_highest_loyalty_channel()

    def random_channel(self):
        nr_channels = len(self.channel_list)
        if nr_channels == 1:
            self.last_random = self.channel_list[0]
        else:
            self.last_random = random.choice([channel for channel in self.channel_list if channel != self.last_random])
        return self.last_random

    # ########### Wondertrade ############

    @property
    def wondertrade_legendaries(self):
        return self.settings["trade_legendaries"]

    @property
    def wondertrade_starters(self):
        return self.settings["trade_starters"]

    @property
    def wondertrade_tiers(self):
        return sorted(self.settings["trade_tiers"], key=lambda x: "0" if x == "S" else x)

    def wondertrade_keep(self, pokemon):
        return self.pokedex.clean_name(pokemon) in self.settings["trade_keep"]

    # ########### Battles ############
    @property
    def auto_battle(self):
        return self.settings["auto_battle"]

    @property
    def auto_battle_challenge(self):
        return self.settings["auto_battle_challenge"]

    @property
    def battle_heal(self):
        return self.settings["battle_heal"]

    @property
    def battle_heal_percent(self):
        return self.settings["battle_heal_percent"]
