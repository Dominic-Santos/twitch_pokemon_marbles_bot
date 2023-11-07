from time import sleep
import traceback
import json

from ..entities.Pokemon import Battle, damage_calculator
from ..entities.Pokemon.Pokedex import Move

from ..ChatLogs import log, log_file
from ..ChatUtils import (
    DISCORD_ALERTS,
    POKEMON,
    seconds_readable,
)


class AutoBattle(object):
    def battle_timer(self):
        thread_name = "Battle Timer"
        log("yellow", f"Thread Created - {thread_name}")

        running = True

        while running:
            try:
                self.auto_battle()
            except KeyboardInterrupt:
                running = False
            except Exception as ex:
                str_ex = str(ex)
                log("red", f"{thread_name} Error - {str_ex}")
                print(traceback.format_exc())
                sleep(10)

        log("yellow", f"Thread Closing - {thread_name}")

    def check_evolve_alert(self, team):
        for pokemon in team:
            poke_obj = self.get_pokemon_stats(pokemon["pokedexId"])

            if poke_obj.evolve_to is None or len(poke_obj.evolve_to.keys()) == 0:
                continue

            limit = poke_obj.evolve_to[poke_obj.evolve_to.keys()[0]]["level"]

            if pokemon["lvl"] >= limit and pokemon["id"] not in POKEMON.ab_evolve_reached:
                POKEMON.ab_evolve_reached.append(pokemon["id"])
                if pokemon["id"] in POKEMON.ab_evolving:

                    msg = f"⚔️ {pokemon['name']} ({poke_obj.name}) is level {limit}, ready to evolve! ⚔️"
                    log("green", msg)
                    POKEMON.discord.post(DISCORD_ALERTS, msg)

            if pokemon["id"] not in POKEMON.ab_evolving:
                POKEMON.ab_evolving.append(pokemon["id"])

    def check_level_alert(self, team):
        limit = POKEMON.settings["alert_level_value"]
        new_level_reached = []

        for pokemon in team:

            if pokemon["lvl"] >= limit and pokemon["id"] not in POKEMON.ab_level_reached:
                POKEMON.ab_level_reached.append(pokemon["id"])
                if pokemon["id"] in POKEMON.ab_training:
                    new_level_reached.append(pokemon)

            if pokemon["id"] not in POKEMON.ab_training:
                POKEMON.ab_training.append(pokemon["id"])

        for pokemon in new_level_reached:
            poke_obj = self.get_pokemon_stats(pokemon["pokedexId"])
            msg = f"⚔️ {pokemon['name']} ({poke_obj.name}) reached level {limit}! ⚔️"
            log("green", msg)
            POKEMON.discord.post(DISCORD_ALERTS, msg)

    def auto_battle(self):
        if POKEMON.auto_battle:

            data = self.pokemon_api.get_battle()

            if data["rejoinableBattle"]:
                log("yellow", f"Rejoining battle")
                self.do_battle()
                return

            team_data = self.pokemon_api.get_teams()

            battle_mode = "stadium"
            difficulty = "hard"

            if POKEMON.auto_battle_challenge and team_data["challenge"] is not None:
                if team_data["challenge"]["error"] == "" or "Try again in" in team_data["challenge"]["error"]:
                    battle_mode = "challenge"
                    difficulty = "medium"
                else:
                    log("red", f"Didn't meet requirements for challenge battle, switching to stadium")

            if battle_mode in team_data:

                if team_data[battle_mode]["error"] == "":
                    remaining = 0
                else:
                    try:
                        time_array = team_data[battle_mode]["error"].split("(")[1].split(" ")
                        if len(time_array) == 5:
                            remaining = 60 * int(time_array[0]) + int(time_array[3])
                        elif "minutes" in time_array:
                            remaining = 60 * int(time_array[0])
                        else:
                            remaining = int(time_array[0])
                    except:
                        remaining = 0

                if remaining > 0:
                    remaining_human = seconds_readable(remaining)
                    log("yellow", f"Next {battle_mode} battle in {remaining_human}")

                sleep(remaining + 1)

                if battle_mode == "stadium":
                    self.get_missions()
                    if POKEMON.missions.check_stadium_mission():
                        difficulty = POKEMON.missions.check_stadium_difficulty()

                team_data = self.pokemon_api.get_teams()
                if team_data[battle_mode]["meet_requirements"]:
                    if POKEMON.settings["alert_level"]:
                        # check team pokemon that reached the desired level
                        self.check_level_alert(team_data["allPokemon"])

                    if POKEMON.settings["alert_evolve"]:
                        # check team pokemon that reached level to evolve
                        self.check_evolve_alert(team_data["allPokemon"])

                    team_id = team_data["teamNumber"]
                    data = self.pokemon_api.battle_create(battle_mode, difficulty, team_id)
                    battle_message = f"{difficulty} {battle_mode}" if battle_mode == "stadium" else battle_mode
                    log("yellow", f"Starting {battle_message} battle")
                    result, key = self.do_battle()
                    if result and battle_mode == "challenge":
                        POKEMON.discord.post(DISCORD_ALERTS, f"⚔️ Won challenge battle {team_data['challenge']['name']} - {key} ⚔️")
                else:
                    log("red", f"Didn't meet requirements for {battle_mode} battle")
                    sleep(15)
            else:
                log("red", f"Error: {battle_mode} not in response")
                sleep(15)
        else:
            sleep(30)

    def do_battle(self):
        battle_data = self.pokemon_api.battle_join()
        battle_connection = self.pokemon_api.battle_connect(battle_data["battle_id"], battle_data["player_id"])
        battle = Battle()
        battle.set_battle(battle_data["battle_id"], battle_data["player_id"], battle_data["unique_battle_key"])
        while battle.state != "end":
            if battle.state == "move":
                # submit a move or switch
                battle.state = "continue"
                pokemon = battle.team["pokemon"][str(battle.team["current_pokemon"])]
                enemy = battle.enemy_team["pokemon"][str(battle.enemy_team["current_pokemon"])]

                move = self.find_best_move(pokemon, enemy)
                payload = {"action": "next_move", "move_id": str(move["move_id"])}
                battle_connection.send(json.dumps(payload))
                sleep(1)

            elif battle.state == "switch":
                # pick a pokemon to switch to
                battle.state = "continue"

                for other_pokemon_id in battle.team["pokemon"]:
                    if other_pokemon_id != str(battle.team["current_pokemon"]):
                        other_pokemon = battle.team["pokemon"][other_pokemon_id]
                        if other_pokemon["hp"] > 0:
                            payload = {"action": "change_pokemon", "battle_pokemon_id": str(other_pokemon_id)}
                            battle_connection.send(json.dumps(payload))
                            sleep(1)
                            break

            resp = battle_connection.recv()
            battle.run_action(resp)
            sleep(0.1)

        if battle.result:
            log_file("green", f"Won the battle! rewards: {battle.rewards}")
        else:
            log_file("red", f"Lost the battle! rewards: {battle.rewards}")

        battle_connection.close()

        return battle.result, battle_data["unique_battle_key"]

    def find_best_move(self, my_pokemon, enemy_pokemon):
        attacker = self.get_pokemon_stats(my_pokemon["pokedex_id"])
        defender = self.get_pokemon_stats(enemy_pokemon["pokedex_id"])

        attacker_moves = my_pokemon["moves"]

        best_move = None
        # best_move = list(attacker_moves.keys())[0]
        best_damage = -1
        best_move_data = Move("struggle", {
            "name": "Struggle",
            "damage_class": "physical",
            "power": 30,
            "pp": 100,
            "type": "Normal"
        })

        for move_id in attacker_moves:
            move = attacker_moves[move_id]

            if move["pp"] > 0:

                move_data = self.get_pokemon_move(move["id"], move["type"])

                # attacker, move data, defender, weather, attacker burned
                min_damage, max_damage = damage_calculator(attacker, move_data, defender, "normal", False)

                if min_damage > best_damage:
                    best_damage = min_damage
                    best_move = move_id
                    best_move_data = move_data

        return {
            "damage": best_damage,
            "move_id": best_move,
            "move_data": best_move_data
        }
