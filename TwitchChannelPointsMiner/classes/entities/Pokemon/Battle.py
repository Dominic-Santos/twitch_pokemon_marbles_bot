import json
from .Utils import check_output_folder, save_to_file
from .Pokemon import Pokemon
from .Pokedex import Move

WEAKNESS_CHART = {
    "Normal": {"Fighting": 2, "Ghost": 0},
    "Fire": {"Fire": 0.5, "Water": 2, "Grass": 0.5, "Ice": 0.5, "Ground": 2, "Bug": 0.5, "Rock": 2, "Steel": 0.5, "Fairy": 0.5},
    "Water": {"Fire": 0.5, "Water": 0.5, "Electric": 2, "Grass": 2, "Ice": 0.5, "Steel": 0.5},
    "Electric": {"Electric": 0.5, "Ground": 2, "Flying": 0.5, "Steel": 0.5},
    "Grass": {"Fire": 2, "Water": 0.5, "Electric": 0.5, "Grass": 0.5, "Ice": 2, "Poison": 2, "Ground": 0.5, "Flying": 2, "Bug": 2},
    "Ice": {"Fire": 2, "Ice": 0.5, "Fighting": 2, "Rock": 2, "Steel": 2},
    "Fighting": {"Flying": 2, "Psychic": 2, "Bug": 0.5, "Rock": 0.5, "Dark": 0.5, "Fairy": 2},
    "Poison": {"Grass": 0.5, "Fighting": 0.5, "Poison": 0.5, "Ground": 2, "Psychic": 2, "Bug": 0.5, "Fairy": 0.5},
    "Ground": {"Water": 2, "Electric": 0, "Grass": 2, "Ice": 2, "Poison": 0.5, "Rock": 0.5},
    "Flying": {"Electric": 2, "Grass": 0.5, "Ice": 2, "Fighting": 0.5, "Ground": 0, "Bug": 0.5, "Rock": 2},
    "Psychic": {"Fighting": 0.5, "Psychic": 0.5, "Bug": 2, "Ghost": 2, "Dark": 2},
    "Bug": {"Fire": 2, "Grass": 0.5, "Fighting": 0.5, "Ground": 0.5, "Flying": 2, "Rock": 2},
    "Rock": {"Normal": 0.5, "Fire": 0.5, "Water": 2, "Grass": 2, "Fighting": 2, "Poison": 0.5, "Ground": 2, "Flying": 0.5, "Steel": 2},
    "Ghost": {"Normal": 0, "Fighting": 0, "Poison": 0.5, "Bug": 0.5, "Ghost": 2, "Dark": 2},
    "Dragon": {"Fire": 0.5, "Water": 0.5, "Electric": 0.5, "Grass": 0.5, "Ice": 2, "Dragon": 2, "Fairy": 2},
    "Dark": {"Fighting": 2, "Psychic": 0, "Bug": 2, "Ghost": 0.5, "Dark": 0.5, "Fairy": 2},
    "Steel": {"Normal": 0.5, "Fire": 2, "Grass": 0.5, "Ice": 0.5, "Fighting": 2, "Poison": 0, "Ground": 2, "Flying": 0.5, "Psychic": 0.5, "Bug": 0.5, "Rock": 0.5, "Dragon": 0.5, "Steel": 0.5, "Fairy": 0.5},
    "Fairy": {"Fighting": 0.5, "Poison": 2, "Bug": 0.5, "Dragon": 0, "Dark": 0.5, "Steel": 2}
}

STATUS = {
    "burn": {
        "applied": "was burned",
        "status": "burned"
    },
    "confusion": {
        "applied": "was confused",
        "status": "confused"
    },
    "freeze": {
        "applied": "was frozen"
    },
    "paralysis": {
        "applied": "was paralyzed",
        "status": "paralyzed"
    },
    "poison": {
        "applied": "was poisoned",
        "status": "poisoned"
    },
    "recoil": {
        "applied": "was hurt by recoil"
    },
    "sleep": {
        "applied": "fell asleep"
    },
    "toxic": {
        "applied": "was badly poisoned"
    },
    "magnet rise": {
        "status": "magnet rise"
    }
}


def weakness_resistance(attack_type, defender_types):
    effective = 1
    for def_type in defender_types:
        effective = effective * WEAKNESS_CHART[def_type].get(attack_type, 1)

    return effective


def damage_calculator(attacker: Pokemon, attack_move: Move, defender: Pokemon, weather: str, burn: bool):
    effective = weakness_resistance(attack_move.move_type, defender.types)

    if attack_move.damage_class == "status" or 0 in [attack_move.power, effective]:
        return 0, 0
    elif attack_move.damage_class == "physical":
        attack = attacker.attack
        defense = defender.defense
        burn_mult = 0.5 if burn else 1
    else:
        attack = attacker.special_attack
        defense = defender.special_defense
        burn_mult = 1

    stab = 1.5 if attack_move.move_type in attacker.types else 1

    if weather == "sun" and attack_move.move_type in ["Fire", "Water"]:
        weather_mult = 1.5 if attack_move.move_type == "Fire" else 0.5
    elif weather == "rain" and attack_move.move_type in ["Fire", "Water"]:
        weather_mult = 1.5 if attack_move.move_type == "Water" else 0.5
    else:
        weather_mult = 1

    damage = ((22.0 * attack_move.power * (attack / defense)) / 50.0 + 2) * burn_mult * stab * weather_mult * effective
    return damage * 0.85, damage


class Battle():
    def __init__(self):
        self.team = {}
        self.enemy_team = {}
        self.action = 0
        self.battle_id = 0
        self.player_id = 0
        self.battle_key = ""
        self.state = "continue"
        self.result = None
        self.rewards = ""
        check_output_folder(f"battles")

    def log(self, line):
        with open(f"battles/{self.battle_id}_{self.battle_key}.log", "a", encoding="utf-8") as f:
            f.write(line + "\n")

    def set_battle(self, battle_id, player_id, unique_battle_key):
        self.battle_id = battle_id
        self.player_id = player_id
        self.battle_key = unique_battle_key

    def save_action(self, data):
        check_output_folder(f"battles/{self.battle_id}_{self.battle_key}")
        save_to_file(f"battles/{self.battle_id}_{self.battle_key}/{self.action}.json", data)

    def submit_move(self, move):
        pokemon = self.team["current_pokemon"]
        self.team["pokemon"][str(pokemon)]["moves"][str(move)]["pp"] = self.team["pokemon"][str(pokemon)]["moves"][str(move)]["pp"] - 1

    def run_action(self, message):
        data = json.loads(message)

        action = data["action"]

        if action in ["INIT", "RE_INIT"]:
            self.action_init(data["content"])
        elif action == "AWAITING_NEXT_MOVE":
            # wait for player to use an attack or switch (or quit)
            if self.state != "submitted":
                self.state = "move"
        elif action == "AWAITING_NEXT_POKEMON":
            # player pokemon died, must switch
            if self.state != "submitted":
                self.state = "switch"
        elif action == "START_LOG":
            # clears the app text, does nothing
            self.log("")
        elif action == "LOG":
            # could be many things
            result = self.action_log(data["content"])
            if result is False:
                self.log(f"Unknown LOG action {data['content']} ({self.action})")
                self.save_action(data)
        elif action == "ANIMATION":
            # animations do nothing
            pass
        elif action == "DAMAGE":
            # damage is delt
            self.action_damage(data["content"])
        elif action == "END":
            # battle ended
            self.action_end(data["content"])
        elif action == "KO":
            # pokemon ko'ed
            self.action_ko(data["content"])
        elif action == "WAIT":
            self.state = "switch"
        elif action == "STOP_TIMER":
            # basically action received
            self.state = "continue"
        elif action == "error":
            self.state = "end"
            self.result = None
            self.error = data["content"]
        else:
            self.log(f"Unknown action {action} ({self.action})")
            self.save_action(data)

        self.action = self.action + 1

    def action_ko(self, data):
        if self.team["current_pokemon"] == data["pokemon"]:
            prefix, pokemon = self._get_pokemon(self.player_id, data["pokemon"])
            self.team["pokemon"][str(data["pokemon"])]["hp"] = 0
        else:
            prefix, pokemon = self._get_pokemon(0, data["pokemon"])
            self.enemy_team["pokemon"][str(data["pokemon"])]["hp"] = 0
        self.log(f"{prefix} {pokemon['name']} fainted")

    def action_end(self, data):
        self.state = "end"
        self.result = True if data["loser"] != self.player_id else False
        prefix = "winner" if self.result else "loser"
        xp = data[prefix + "_xp"]
        cash = data[prefix + "_cash"]
        self.rewards = f"{xp}Exp and {cash}$"
        self.log(f"\nYou are the {prefix}!\nYou got {self.rewards}")

    def action_damage(self, data):
        self._apply_damage(data["player"], data["pokemon"], data["damage"])
        prefix, pokemon = self._get_pokemon(data["player"], data["pokemon"])

        self.log(f"{prefix} {pokemon['name']} took {data['damage']} damage")
        self.log(f"Current HP {pokemon['hp']}/{pokemon['max_hp']}")

    def _get_pokemon(self, player, pokemon):
        if player == self.player_id:
            prefix = "My"
            pokemon = self.team["pokemon"][str(pokemon)]
        else:
            prefix = "Enemy"
            pokemon = self.enemy_team["pokemon"][str(pokemon)]

        return prefix, pokemon

    def _apply_damage(self, player, pokemon, damage):
        if player == self.player_id:
            self.team["pokemon"][str(pokemon)]["hp"] = self.team["pokemon"][str(pokemon)]["hp"] - damage
        else:
            self.enemy_team["pokemon"][str(pokemon)]["hp"] = self.enemy_team["pokemon"][str(pokemon)]["hp"] - damage

    def _use_move(self, player, pokemon, move, move_name):
        if player == self.player_id:
            if str(move) not in self.team["pokemon"][str(pokemon)]["moves"]:
                return "Struggle"
            self.team["pokemon"][str(pokemon)]["moves"][str(move)]["pp"] = self.team["pokemon"][str(pokemon)]["moves"][str(move)]["pp"] - 1
            return self.team["pokemon"][str(pokemon)]["moves"][str(move)]["name"]
        else:
            return move_name
            # NO MORE ENEMY MOVES
            # if str(move) not in self.enemy_team["pokemon"][str(pokemon)]["moves"]:
            #     return "Struggle"
            # self.enemy_team["pokemon"][str(pokemon)]["moves"][str(move)]["pp"] = self.enemy_team["pokemon"][str(pokemon)]["moves"][str(move)]["pp"] - 1
            # return self.enemy_team["pokemon"][str(pokemon)]["moves"][str(move)]["name"]

    @staticmethod
    def clean_action(action, to_replace):
        return action.lower().replace(to_replace.lower(), "").replace("_", " ").strip()

    def action_log(self, data):
        prefix, pokemon = (None, None)
        if "player" in data and "pokemon" in data:
            prefix, pokemon = self._get_pokemon(data["player"], data["pokemon"])

        typ = data["type"]

        if typ.endswith("APPLIED") and self.clean_action(typ, "applied") in STATUS:
            # BURN_APPLIED, etc
            ctyp = self.clean_action(typ, "applied")
            effect = STATUS[ctyp]["applied"]
            if prefix is None:
                effect = effect[0].title() + effect[1:]
                self.log(effect)
            else:
                self.log(f"{prefix} {pokemon['name']} {effect}")
        elif typ.endswith("DAMAGE"):
            # BURN_DAMAGE, HAIL_DAMAGE, POISON_DAMAGE, SANDSTORM_DAMAGE
            effect = self.clean_action(typ, "damage")
            self._apply_damage(data["player"], data["pokemon"], data["damage"])
            prefix, pokemon = self._get_pokemon(data["player"], data["pokemon"])
            self.log(f"{prefix} {pokemon['name']} took {data['damage']} {effect} damage")
            self.log(f"Current HP {pokemon['hp']}/{pokemon['max_hp']}")
        elif typ.startswith("END") and self.clean_action(typ, "end") in STATUS:
            # END_BURN, etc
            ctyp = self.clean_action(typ, "end")
            effect = STATUS[ctyp]["status"]
            self.log(f"{prefix} {pokemon['name']} is no longer {effect}")
        elif typ in [
            "ATTACK_MISSED", "CRITICAL_HIT", "HAIL_END", "HAIL_STARTED", "HAZE_USED",
            "LIGHT_SCREEN_END", "LIGHT_SCREEN_STARTED", "MIST_END", "MIST_PREVENTED",
            "MIST_STARTED", "MOVE_FAILED", "RAIN_END", "RAIN_STARTED", "REFLECT_END",
            "REFLECT_STARTED", "SANDSTORM_END", "SANDSTORM_STARTED", "SUN_END", "SUN_STARTED",
            "TAILWIND_END", "TAILWIND_STARTED", "TRICK_ROOM_STARTED", "TRICK_ROOM_END",
            "TAUNTED_STARTED", "TAUNTED_END"
        ]:
            self.log(typ.replace("_", " ").title().replace("End", "Ended"))
        elif typ in ["CONFUSED", "UNTHAWED", "WOKE_UP", "FLINCHED", "IS_FROZEN", "IS_PARALYZED", "IS_SLEEPING"]:
            effect = typ.replace("_", " ").title()
            self.log(f"{prefix} {pokemon['name']} {effect}")
        elif typ == "ALLOW_SWITCHING":
            self.log(f"{prefix} {pokemon['name']} can switch")
        elif typ == "DISALLOW_SWITCHING":
            self.log(f"{prefix} {pokemon['name']} is not allowed to switch")
        elif typ == "HEALED":
            self._apply_damage(data["player"], data["pokemon"], 0 - data["heal"])
            prefix, pokemon = self._get_pokemon(data["player"], data["pokemon"])
            self.log(f"{prefix} {pokemon['name']} healed {data['heal']} damage")
            self.log(f"Current HP {pokemon['hp']}/{pokemon['max_hp']}")
        elif typ == "MOVE_EFFECTIVE":
            self.log(f"Effective x{data['factor']}")
        elif typ == "MOVE_USED":
            move_name = self._use_move(data["player"], data["pokemon"], data["move"], data.get("moveName", ""))
            self.log(f"{prefix} {pokemon['name']} used {move_name}")
        elif typ == "MOVE_USED_NAME":
            self.log(f"{prefix} {pokemon['name']} used {data['move']}")
        elif typ == "MULTIPLE_HITS":
            self.log(f"Attack hit {data['amount']} times")
        elif typ == "POKEMON_CHANGED":
            if self.team["current_pokemon"] == data["last_pokemon"]:
                prefix, last = self._get_pokemon(self.player_id, data["last_pokemon"])
                prefix, current = self._get_pokemon(self.player_id, data["current_pokemon"])
                self.team["current_pokemon"] = data["current_pokemon"]
            else:
                prefix, last = self._get_pokemon(0, data["last_pokemon"])
                self.enemy_team["current_pokemon"] = data["current_pokemon"]
                self.enemy_team["pokemon"][str(data["current_pokemon"])] = data["current_pokemon_data"]
                prefix, current = self._get_pokemon(0, data["current_pokemon"])
            self.log(f"Switched {prefix} {last['name']} for {current['name']}")
            self.log(f"Current HP {current['hp']}/{current['max_hp']}")
        elif typ == "STAT_CHANGED":
            self.log(f"{prefix} {pokemon['name']} {data['stat']} changed by {data['change_by']}")
        else:
            return False
        return True

    def action_init(self, data):
        self.log("Connected to Battle\n")

        for player in data["players"]:
            if player == str(self.player_id):
                self.team = data["players"][player]
            else:
                self.enemy_team = data["players"][player]

        for team in [self.team, self.enemy_team]:
            for pokemon_id in team["pokemon"]:
                pokemon_data = team["pokemon"][pokemon_id]
                poke_name = "?" if pokemon_data['name'] is None else pokemon_data['name']
                self.log(f"{poke_name} {pokemon_data['hp']}/{pokemon_data['max_hp']}")
            self.log("")
