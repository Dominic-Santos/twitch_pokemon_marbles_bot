import random
from datetime import datetime, timedelta
import json

from .Discord import Discord
from .Missions import Missions, VALID_TYPES
from .Inventory import Inventory
from .Pokedex import Pokedex
from .Computer import Computer
from .Loyalty import Loyalty

SETTINGS_FILE = "pokemon.json"

WONDERTRADE_DELAY = 60 * 60 * 3 + 60  # 3 hours and 1 min (just in case)
POKEDAILY_DELAY = 60 * 60 * 20 + 60  # 20 hours and 1 min


class PokemonComunityGame(Loyalty):
    def __init__(self):
        Loyalty.__init__(self)

        self.delay = 0
        self.reset_timer()
        self.wondertrade_timer = None
        self.pokedaily_timer = None
        self.last_random = None

        self.channel_list = []
        self.online_channels = []

        self.discord = Discord()
        self.inventory = Inventory()
        self.pokedex = Pokedex()
        self.missions = Missions()
        self.missions.new_missions_callback = self.save_settings
        self.computer = Computer()

        self.default_settings = {
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
                "values": [self.pokedex.stats(str(x)).name for x in range(1, self.pokedex.total + 1)],
            },
            "catch_tiers": {
                "value": [],
                "hint": "Catch any pokemon of the selected tiers",
                "values": ["S", "A", "B", "C"],
            },
            "catch_types": {
                "value": [],
                "hint": "Catch any pokemon of the selected types",
                "values": VALID_TYPES,
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
                "values": [self.pokedex.stats(str(x)).name for x in range(1, self.pokedex.total + 1)],
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

    def set_delay(self, delay):
        self.delay = delay

    def need_pokemon(self, pokemon):
        reasons = []

        dexneed = self.pokedex.need(pokemon)
        if dexneed in [True, None]:
            reasons.append("pokedex")
            if dexneed is None:
                reasons.append("pokedex_error")

        if self.settings["complete_bag"]:
            if self.computer.need(pokemon):
                reasons.append("bag")

        if self.settings["catch_alternates"]:
            if self.pokedex.need_alt(pokemon):
                reasons.append("alt")

        missions = self.missions.check_all_missions(pokemon)
        for mission in missions:
            reasons.append(mission)

        if self.pokedex.clean_name(pokemon) in self.settings["catch"]:
            reasons.append("catch")

        for poke_type in pokemon.types:
            if poke_type in self.settings["catch_types"]:
                reasons.append("all_type")
                break

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

        strategy = "worst"
        for reason in reasons:
            if self.missions.mission_best_ball(reason):
                strategy = "best"
                break
        if strategy == "best":
            if self.inventory.cash < self.settings["money_saving"]:
                strategy = "save"

        if len(reasons) == 1 and "spend_money" in reasons:
            # if the only reason is to spend money, then apply the selected strategy
            strategy = self.settings["spend_money_strategy"]

        return reasons, strategy

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

    def reset_wondertrade_timer(self):
        self.wondertrade_timer = datetime.utcnow()

    def check_wondertrade(self):
        if self.wondertrade_timer is None:
            return False

        if (datetime.utcnow() - self.wondertrade_timer).total_seconds() > WONDERTRADE_DELAY:
            return True

        return False

    def check_wondertrade_left(self):
        return timedelta(seconds=WONDERTRADE_DELAY) - (datetime.utcnow() - self.wondertrade_timer)

    @property
    def wondertrade_legendaries(self):
        return self.settings["trade_legendaries"]

    @property
    def wondertrade_starters(self):
        return self.settings["trade_starters"]

    def wondertrade_keep(self, pokemon):
        return self.pokedex.clean_name(pokemon) in self.settings["trade_keep"]

    # ########### Battles ############
    @property
    def auto_battle(self):
        return self.settings["auto_battle"]

    @property
    def auto_battle_challenge(self):
        return self.settings["auto_battle_challenge"]

    # ########### Pokedaily ############

    def reset_pokedaily_timer(self):
        self.pokedaily_timer = datetime.utcnow()

    def check_pokedaily(self):
        if self.pokedaily_timer is None:
            return False

        if (datetime.utcnow() - self.pokedaily_timer).total_seconds() > POKEDAILY_DELAY:
            return True

        return False

    def check_pokedaily_left(self):
        return timedelta(seconds=POKEDAILY_DELAY) - (datetime.utcnow() - self.pokedaily_timer)
