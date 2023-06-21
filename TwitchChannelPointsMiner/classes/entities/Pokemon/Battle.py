import jwt
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


def decode(data):
    try:
        decoded = jwt.decode(data, options={"verify_signature": False})
        return json.loads(decoded["content"])
    except Exception as e:
        print(e)
    return None


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

    def run_action(self, data):
        self.state = "continue"

        if "data" in data:
            data["decoded"] = decode(data["data"])

        action = data["action"]

        if action in ["INIT", "RE_INIT"]:
            self.action_init(data["decoded"])
        elif action == "AWAITING_NEXT_MOVE":
            # wait for player to use an attack or switch (or quit)
            self.state = "move"
        elif action == "AWAITING_NEXT_POKEMON":
            # player pokemon died, must switch
            self.state = "switch"
        elif action == "START_LOG":
            # clears the app text, does nothing
            self.log("")
        elif action == "LOG":
            # could be many things
            result = self.action_log(data["decoded"])
            if result is False:
                self.log(f"Unknown LOG action {data['decoded']['type']} ({self.action})")
                self.save_action(data)
        elif action == "ANIMATION":
            # animations do nothing
            pass
        elif action == "DAMAGE":
            # damage is delt
            self.action_damage(data["decoded"])
        elif action == "END":
            # battle ended
            self.action_end(data["decoded"])
        elif action == "KO":
            # pokemon ko'ed
            self.action_ko(data["decoded"])
        elif action == "WAIT":
            self.state = "switch"
        else:
            self.log(f"Unknown action {action} ({self.action})")
            self.save_action(data)

        self.action = self.action + 1
        # maybe remove this if all goes well with testing

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

    def _use_move(self, player, pokemon, move):
        if player == self.player_id:
            if str(move) not in self.team["pokemon"][str(pokemon)]["moves"]:
                print("-------------------Struggle", self.team["pokemon"][str(pokemon)])
                return "Struggle"
            # self.team["pokemon"][str(pokemon)]["moves"][str(move)]["pp"] = self.team["pokemon"][str(pokemon)]["moves"][str(move)]["pp"] - 1
            return self.team["pokemon"][str(pokemon)]["moves"][str(move)]["name"]
        else:
            if str(move) not in self.enemy_team["pokemon"][str(pokemon)]["moves"]:
                print("-------------------Struggle", self.enemy_team["pokemon"][str(pokemon)])
                return "Struggle"
            self.enemy_team["pokemon"][str(pokemon)]["moves"][str(move)]["pp"] = self.enemy_team["pokemon"][str(pokemon)]["moves"][str(move)]["pp"] - 1
            return self.enemy_team["pokemon"][str(pokemon)]["moves"][str(move)]["name"]

    def action_log(self, data):
        if "player" in data and "pokemon" in data:
            prefix, pokemon = self._get_pokemon(data["player"], data["pokemon"])

        typ = data["type"]

        if typ == "ALLOW_SWITCHING":
            self.log("Switching is now allowed")
        elif typ == "ATTACK_MISSED":
            self.log(f"Attack missed")
        elif typ == "BURN_APPLIED":
            self.log(f"{prefix} {pokemon['name']} was burned")
        elif typ == "BURN_DAMAGE":
            self._apply_damage(data["player"], data["pokemon"], data["damage"])
            prefix, pokemon = self._get_pokemon(data["player"], data["pokemon"])
            self.log(f"{prefix} {pokemon['name']} took {data['damage']} burn damage")
            self.log(f"Current HP {pokemon['hp']}/{pokemon['max_hp']}")
        elif typ == "CONFUSED":
            self.log(f"{prefix} {pokemon['name']} is confused")
        elif typ == "CONFUSION_APPLIED":
            self.log(f"{prefix} {pokemon['name']} was confused")
        elif typ == "CRITICAL_HIT":
            self.log("Critical Hit")
        elif typ == "DISALLOW_SWITCHING":
            self.log("Switching is not allowed")
        elif typ == "END_CONFUSION":
            self.log(f"{prefix} {pokemon['name']} is not confused anymore")
        elif typ == "END_BURN":
            self.log(f"{prefix} {pokemon['name']} no longer burned")
        elif typ == "END_MAGNET_RISE":
            self.log(f"{prefix} {pokemon['name']} magnet rise ended")
        elif typ == "END_PARALYSIS":
            self.log(f"{prefix} {pokemon['name']} no longer paralyzed")
        elif typ == "FLINCHED":
            self.log(f"{prefix} {pokemon['name']} flinched")
        elif typ == "FREEZE_APPLIED":
            self.log(f"{prefix} {pokemon['name']} was frozen")
        elif typ == "HAIL_DAMAGE":
            self._apply_damage(data["player"], data["pokemon"], data["damage"])
            prefix, pokemon = self._get_pokemon(data["player"], data["pokemon"])
            self.log(f"{prefix} {pokemon['name']} took {data['damage']} hail damage")
            self.log(f"Current HP {pokemon['hp']}/{pokemon['max_hp']}")
        elif typ == "HAIL_STARTED":
            self.log("Hail started")
        elif typ == "HAZE_USED":
            self.log("Haze used")
        elif typ == "HEALED":
            self._apply_damage(data["player"], data["pokemon"], 0 - data["heal"])
            prefix, pokemon = self._get_pokemon(data["player"], data["pokemon"])
            self.log(f"{prefix} {pokemon['name']} healed {data['heal']} damage")
            self.log(f"Current HP {pokemon['hp']}/{pokemon['max_hp']}")
        elif typ == "IS_FROZEN":
            self.log(f"{prefix} {pokemon['name']} is frozen")
        elif typ == "IS_PARALYZED":
            self.log(f"{prefix} {pokemon['name']} can't attack due to paralysis")
        elif typ == "IS_SLEEPING":
            self.log(f"{prefix} {pokemon['name']} is asleep")
        elif typ == "LIGHT_SCREEN_END":
            self.log("Light Screen ended")
        elif typ == "LIGHT_SCREEN_STARTED":
            self.log("Light Screen started")
        elif typ == "MIST_END":
            self.log("Mist ended")
        elif typ == "MIST_STARTED":
            self.log("Mist started")
        elif typ == "MOVE_EFFECTIVE":
            self.log(f"Effective x{data['factor']}")
        elif typ == "MOVE_FAILED":
            self.log("Move Failed")
        elif typ == "MOVE_USED":
            move_name = self._use_move(data["player"], data["pokemon"], data["move"])
            self.log(f"{prefix} {pokemon['name']} used {move_name}")
        elif typ == "MOVE_USED_NAME":
            self.log(f"{prefix} {pokemon['name']} used {data['move']}")
        elif typ == "MULTIPLE_HITS":
            self.log(f"Attack hit {data['amount']} times")
        elif typ == "PARALYSIS_APPLIED":
            self.log(f"{prefix} {pokemon['name']} was paralyzed")
        elif typ == "POISON_APPLIED":
            self.log(f"{prefix} {pokemon['name']} was poisoned")
        elif typ == "POISON_DAMAGE":
            self._apply_damage(data["player"], data["pokemon"], data["damage"])
            prefix, pokemon = self._get_pokemon(data["player"], data["pokemon"])
            self.log(f"{prefix} {pokemon['name']} took {data['damage']} poison damage")
            self.log(f"Current HP {pokemon['hp']}/{pokemon['max_hp']}")
        elif typ == "POKEMON_CHANGED":
            if self.team["current_pokemon"] == data["last_pokemon"]:
                prefix, last = self._get_pokemon(self.player_id, data["last_pokemon"])
                prefix, current = self._get_pokemon(self.player_id, data["current_pokemon"])
                self.team["current_pokemon"] = data["current_pokemon"]
            else:
                prefix, last = self._get_pokemon(0, data["last_pokemon"])
                prefix, current = self._get_pokemon(0, data["current_pokemon"])
                self.enemy_team["current_pokemon"] = data["current_pokemon"]
            self.log(f"Switched {prefix} {last['name']} for {current['name']}")
            self.log(f"Current HP {current['hp']}/{current['max_hp']}")
        elif typ == "RAIN_END":
            self.log("Rain ended")
        elif typ == "RAIN_STARTED":
            self.log("Rain started")
        elif typ == "RECOIL_APPLIED":
            self.log("Hurt by recoil")
        elif typ == "REFLECT_END":
            self.log("Reflect ended")
        elif typ == "REFLECT_STARTED":
            self.log("Reflect started")
        elif typ == "SANDSTORM_DAMAGE":
            self._apply_damage(data["player"], data["pokemon"], data["damage"])
            prefix, pokemon = self._get_pokemon(data["player"], data["pokemon"])
            self.log(f"{prefix} {pokemon['name']} took {data['damage']} sandstorm damage")
            self.log(f"Current HP {pokemon['hp']}/{pokemon['max_hp']}")
        elif typ == "SANDSTORM_END":
            self.log("Sandstorm ended")
        elif typ == "SANDSTORM_STARTED":
            self.log("Sandstorm started")
        elif typ == "SLEEP_APPLIED":
            self.log(f"{prefix} {pokemon['name']} fell asleep")
        elif typ == "STAT_CHANGED":
            self.log(f"{prefix} {pokemon['name']} {data['stat']} changed by {data['change_by']}")
        elif typ == "SUN_END":
            self.log("Sun ended")
        elif typ == "SUN_STARTED":
            self.log("Sun started")
        elif typ == "TAILWIND_END":
            self.log("Tailwind ended")
        elif typ == "TAILWIND_STARTED":
            self.log("Tailwind started")
        elif typ == "TOXIC_APPLIED":
            self.log(f"{prefix} {pokemon['name']} was badly poisoned")
        elif typ == "TRICK_ROOM_STARTED":
            self.log("Trick room started")
        elif typ == "TRICK_ROOM_END":
            self.log("Trick room ended")
        elif typ == "UNTHAWED":
            self.log(f"{prefix} {pokemon['name']} unthawed")
        elif typ == "WOKE_UP":
            self.log(f"{prefix} {pokemon['name']} woke up")
        else:
            return False
        return True

    def action_init(self, data):
        if "actionNo" in data:
            self.action = data["actionNo"] - 1
            self.log("Reconnected to Battle\n")
        else:
            self.log("Connected to Battle\n")

        for player in data["players"]:
            if player == str(self.player_id):
                self.team = data["players"][player]
            else:
                self.enemy_team = data["players"][player]

        for team in [self.team, self.enemy_team]:
            for pokemon_id in team["pokemon"]:
                pokemon_data = team["pokemon"][pokemon_id]
                self.log(f"{pokemon_data['name']} {pokemon_data['hp']}/{pokemon_data['max_hp']}")
            self.log("")
