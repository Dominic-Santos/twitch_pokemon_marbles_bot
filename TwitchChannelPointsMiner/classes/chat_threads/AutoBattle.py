import traceback
from time import sleep
import copy

from ..entities.Pokemon import Battle, damage_calculator
from ..entities.Pokemon.Pokedex import Move


from ..ChatUtils import (
    DISCORD_ALERTS,
    log,
    log_file,
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
        battle = Battle()
        battle.set_battle(battle_data["battle_id"], battle_data["player_id"], battle_data["unique_battle_key"])
        while battle.state != "end":
            if battle.state == "move":
                # submit a move or switch
                battle.state = "continue"
                pokemon = battle.team["pokemon"][str(battle.team["current_pokemon"])]
                enemy = battle.enemy_team["pokemon"][str(battle.enemy_team["current_pokemon"])]

                result = self.matchup_winner(pokemon, enemy)

                if result["win"]:
                    if result["move"] is None:
                        result["move"] = list(pokemon["moves"].keys())[0]
                    self.pokemon_api.battle_submit_move(battle.battle_id, result["move"])
                    sleep(1)
                    continue

                elif pokemon["hp"] > pokemon["max_hp"] / 2:
                    best_result = None
                    best_switch_id = None
                    for other_pokemon_id in battle.team["pokemon"]:
                        if other_pokemon_id != str(battle.team["current_pokemon"]):
                            other_pokemon = battle.team["pokemon"][other_pokemon_id]
                            if other_pokemon["hp"] > 0:
                                swap = False
                                switch_result = self.matchup_winner(other_pokemon, enemy, True)

                                if best_result is None:
                                    swap = True
                                elif switch_result["win"]:
                                    if switch_result["win"] != best_result["win"]:
                                        swap = True
                                    elif switch_result["win"]:
                                        if switch_result["taken"] < best_result["taken"]:
                                            swap = True
                                    else:
                                        if switch_result["dealt"] > best_result["dealt"]:
                                            swap = True

                                if swap:
                                    best_switch_id = other_pokemon_id
                                    best_result = switch_result

                    if best_result is not None:
                        if best_result["win"]:
                            self.pokemon_api.battle_switch_pokemon(battle.battle_id, best_switch_id)
                            sleep(1)
                            continue

                # battle.submit_move(result["move"])
                self.pokemon_api.battle_submit_move(battle.battle_id, result["move"])
                sleep(1)

            elif battle.state == "switch":
                # pick a pokemon to switch to
                battle.state = "continue"

                enemy = battle.enemy_team["pokemon"][str(battle.enemy_team["current_pokemon"])]
                best_result = None
                best_switch_id = None
                for other_pokemon_id in battle.team["pokemon"]:
                    if other_pokemon_id != str(battle.team["current_pokemon"]):
                        other_pokemon = battle.team["pokemon"][other_pokemon_id]
                        if other_pokemon["hp"] > 0:
                            swap = False
                            switch_result = self.matchup_winner(other_pokemon, enemy, True)

                            if best_result is None:
                                swap = True
                            elif switch_result["win"]:
                                if switch_result["win"] != best_result["win"]:
                                    swap = True
                                elif switch_result["win"]:
                                    if switch_result["taken"] < best_result["taken"]:
                                        swap = True
                                else:
                                    if switch_result["dealt"] > best_result["dealt"]:
                                        swap = True

                            if swap:
                                best_switch_id = other_pokemon_id
                                best_result = switch_result
                if best_result is None:
                    battle.state = "move"
                    continue
                self.pokemon_api.battle_switch_pokemon(battle.battle_id, best_switch_id)
                sleep(1)

            resp = self.pokemon_api.battle_action(battle.action, battle.battle_id, battle.player_id)
            battle.run_action(resp)
            sleep(0.1)

        if battle.result:
            log_file("green", f"Won the battle! rewards: {battle.rewards}")
        else:
            log_file("red", f"Lost the battle! rewards: {battle.rewards}")

        return battle.result, battle_data["unique_battle_key"]

    def matchup_winner(self, my, enemy, switched=False):
        my_pokemon = copy.deepcopy(my)
        enemy_pokemon = copy.deepcopy(enemy)
        my_stats = self.get_pokemon_stats(my_pokemon["pokedex_id"])
        enemy_stats = self.get_pokemon_stats(enemy_pokemon["pokedex_id"])
        skip = switched
        move = None

        # run until one is dead
        while my_pokemon["hp"] > 0 and enemy_pokemon["hp"] > 0:
            my_move = self.find_best_move(my_stats, my_pokemon["moves"], enemy_stats)
            enemy_move = self.find_best_move(enemy_stats, enemy_pokemon["moves"], my_stats)

            if move is None:
                move = my_move

            if my_move["move_id"] is None:
                # attacker, move data, defender, weather, attacker burned
                my_move["damage"] = damage_calculator(my_stats, my_move["move_data"], enemy_stats, "normal", False)[0]
            elif skip is False:
                my_pokemon["moves"][my_move["move_id"]]["pp"] = my_pokemon["moves"][my_move["move_id"]]["pp"] - 1

            if enemy_move["move_id"] is None:
                # attacker, move data, defender, weather, attacker burned
                enemy_move["damage"] = damage_calculator(enemy_stats, my_move["move_data"], my_stats, "normal", False)[0]
            else:
                enemy_pokemon["moves"][enemy_move["move_id"]]["pp"] = enemy_pokemon["moves"][enemy_move["move_id"]]["pp"] - 1

            if my_move["move_data"].priority > enemy_move["move_data"].priority or (
                my_move["move_data"].priority == enemy_move["move_data"].priority and my_stats.speed > enemy_stats.speed
            ):
                # I attack first
                if skip:
                    skip = False
                else:
                    enemy_pokemon["hp"] = enemy_pokemon["hp"] - my_move["damage"]
                    if enemy_pokemon["hp"] <= 0:
                        continue

                my_pokemon["hp"] = my_pokemon["hp"] - enemy_move["damage"]
            else:
                # enemy attacks first
                my_pokemon["hp"] = my_pokemon["hp"] - enemy_move["damage"]
                if my_pokemon["hp"] <= 0:
                    continue

                if skip:
                    skip = False
                else:
                    enemy_pokemon["hp"] = enemy_pokemon["hp"] - my_move["damage"]
        return {
            "win": my_pokemon["hp"] > 0,
            "dealt": enemy["hp"] - enemy_pokemon["hp"],
            "taken": my["hp"] - my_pokemon["hp"],
            "move": "" if move is None else move["move_id"]
        }

    def find_best_move(self, attacker, attacker_moves, defender):
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
