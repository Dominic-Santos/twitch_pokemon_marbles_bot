from time import sleep
import traceback
from datetime import datetime
from dateutil.parser import parse


from ..ChatUtils import (
    CHARACTERS,
    DISCORD_STATS,
    log,
    LOGFILE,
    POKEMON,
)


def get_battle_logs(the_date):
    total_exp = 0
    total_cash = 0
    total_battles = 0
    total_wins = 0

    with open(LOGFILE, mode="rb") as file:
        for uline in file:
            try:
                line = uline.decode("utf-8").rstrip()
            except:
                continue

            if "the battle!" not in line:
                continue

            linedate = parse(line.split(" ")[0])
            if linedate.date() != the_date:
                continue

            rewards = line.split("rewards: ")[1].split(" and ")
            exp = int(rewards[0][:-3])
            cash = int(rewards[1][:-1])

            total_exp += exp
            total_cash += cash
            total_battles += 1
            if "Won" in line:
                total_wins += 1

    return {
        "cash": total_cash,
        "exp": total_exp,
        "battles": total_battles,
        "wins": total_wins,
    }


class DailyTasks(object):

    def daily_task_timer(self):
        thread_name = "Daily Task"
        log("yellow", f"Thread Created - {thread_name}")
        running = True
        previous = None

        while running:
            try:
                cur_date = datetime.now().date()
                if cur_date != previous:
                    self.daily_tasks(previous, cur_date)
                    previous = cur_date
            except KeyboardInterrupt:
                running = False
            except Exception as ex:
                str_ex = str(ex)
                log("red", f"{thread_name} Error - {str_ex}")
                print(traceback.format_exc())
            sleep(15 * 60)  # 15 mins

        log("yellow", f"Thread Closing - {thread_name}")

    def daily_tasks(self, previous_date, current_date):
        log("yellow", f"Running Daily Tasks")
        self.stats_computer(previous_date, current_date)
        self.check_bag_pokemon()
        self.check_finish_pokedex()

    def stats_computer(self, previous_date, current_date):

        all_pokemon = self.pokemon_api.get_all_pokemon()
        POKEMON.sync_computer(all_pokemon)

        dex = self.pokemon_api.get_pokedex()
        POKEMON.sync_pokedex(dex)

        inv = self.pokemon_api.get_inventory()
        POKEMON.sync_inventory(inv)

        allpokemon = POKEMON.computer.pokemon

        spawnables_a = []
        spawnables_b = []
        spawnables_c = []

        for i in range(1, POKEMON.pokedex.total + 1):
            pokemon = self.get_pokemon_stats(i)

            if pokemon.is_starter or pokemon.is_legendary or pokemon.is_non_spawnable:
                continue

            if pokemon.tier == "A":
                spawnables_a.append(pokemon)
            elif pokemon.tier == "B":
                spawnables_b.append(pokemon)
            elif pokemon.tier == "C":
                spawnables_c.append(pokemon)

        spawnables_a_total = len(spawnables_a)
        spawnables_b_total = len(spawnables_b)
        spawnables_c_total = len(spawnables_c)

        spawnables_total = spawnables_a_total + spawnables_b_total + spawnables_c_total

        spawnables_a_have = len([pokemon for pokemon in spawnables_a if POKEMON.pokedex.have(pokemon)])
        spawnables_b_have = len([pokemon for pokemon in spawnables_b if POKEMON.pokedex.have(pokemon)])
        spawnables_c_have = len([pokemon for pokemon in spawnables_c if POKEMON.pokedex.have(pokemon)])
        spawnables_a_dont_have = [pokemon for pokemon in spawnables_a if POKEMON.pokedex.have(pokemon) is False]
        spawnables_b_dont_have = [pokemon for pokemon in spawnables_b if POKEMON.pokedex.have(pokemon) is False]
        spawnables_c_dont_have = [pokemon for pokemon in spawnables_c if POKEMON.pokedex.have(pokemon) is False]
        spawnables_have = spawnables_a_have + spawnables_b_have + spawnables_c_have

        spawnables_per = int(spawnables_have * 10000.0 / spawnables_total) / 100.0
        spawnables_a_per = int(spawnables_a_have * 10000.0 / spawnables_a_total) / 100.0
        spawnables_b_per = int(spawnables_b_have * 10000.0 / spawnables_b_total) / 100.0
        spawnables_c_per = int(spawnables_c_have * 10000.0 / spawnables_c_total) / 100.0

        results = {
            "shiny": [],
            "starter": [],
            "female": [],
            "legendary": [],
            "non_spawnable": [],
            "bag_regular": [],
            "bag_special": [],
        }

        for pokemon in allpokemon:
            if pokemon["isShiny"]:
                results["shiny"].append(pokemon)

            pokeobj = self.get_pokemon_stats(pokemon["pokedexId"])
            if pokeobj.is_starter:
                results["starter"].append(pokeobj.pokedex_id)
            if pokeobj.is_female:
                results["female"].append(pokeobj.pokedex_id)
            if pokeobj.is_legendary:
                results["legendary"].append(pokeobj.pokedex_id)
            if pokeobj.is_non_spawnable:
                results["non_spawnable"].append(pokeobj.pokedex_id)
            if pokeobj.pokedex_id <= POKEMON.pokedex.total:
                results["bag_regular"].append(pokeobj.pokedex_id)
            else:
                results["bag_special"].append(pokeobj.pokedex_id)

        results["shiny"] = len(results["shiny"])
        for k in ["starter", "female", "legendary", "bag_regular", "bag_special", "non_spawnable"]:
            results[k] = len(set(results[k]))

        for tier in ["S", "A", "B", "C"]:
            results[f"trade{tier}"] = len([pokemon for pokemon in allpokemon if pokemon["nickname"] is not None and f"trade{tier}" in pokemon["nickname"]])

        region_msg_list = []
        prefixes = POKEMON.pokedex.prefixes
        for region in prefixes:
            num = len(set([pokemon["pokedexId"] for pokemon in allpokemon if pokemon["name"].startswith(prefixes[region] + " ")]))
            if num > 0:
                region_msg_list.append((region, num, getattr(POKEMON.pokedex, region.lower())))

        region_msg = "".join([f"\n    {region}: {num}/{total}" for region, num, total in region_msg_list])

        tradable_total = sum([results[f"trade{tier}"] for tier in ["A", "B", "C"]])

        cash = POKEMON.inventory.cash
        pokeball = POKEMON.inventory.balls.get("pokeball", 0)
        premierball = POKEMON.inventory.balls.get("premierball", 0)
        greatball = POKEMON.inventory.balls.get("greatball", 0)
        ultraball = POKEMON.inventory.balls.get("ultraball", 0)
        otherball = sum([value for key, value in POKEMON.inventory.balls.items() if key not in ["pokeball", "premierball", "greatball", "ultraball"]])

        if POKEMON.inventory.have_item("battle coin"):
            coins = POKEMON.inventory.get_item("battle coin")["amount"]
        else:
            coins = 0

        max_show_missing = 20

        if len(spawnables_a_dont_have) == 0:
            missing_a_string = "Done"
        elif len(spawnables_a_dont_have) in range(0, max_show_missing):
            missing_a_string = "missing: " + ", ".join([pokemon.name for pokemon in spawnables_a_dont_have])
        else:
            missing_a_string = ""

        if len(spawnables_b_dont_have) == 0:
            missing_b_string = "Done"
        elif len(spawnables_b_dont_have) in range(0, max_show_missing):
            missing_b_string = "missing: " + ", ".join([pokemon.name for pokemon in spawnables_b_dont_have])
        else:
            missing_b_string = ""

        if len(spawnables_c_dont_have) == 0:
            missing_c_string = "Done"
        elif len(spawnables_c_dont_have) in range(0, max_show_missing):
            missing_c_string = "missing: " + ", ".join([pokemon.name for pokemon in spawnables_c_dont_have])
        else:
            missing_c_string = ""

        battle_date = previous_date if previous_date is not None else current_date
        battle_stats = get_battle_logs(battle_date)

        discord_msg = f"""Bag Summary:

Starters: {results["starter"]}
Legendary: {results["legendary"]}
Non-Spawnables: {results["non_spawnable"]}/{POKEMON.pokedex.non_spawnables}
Shiny: {results["shiny"]}

Normal Version: {results["bag_regular"]}/{POKEMON.pokedex.total}
Alt Version: {results["bag_special"]}
    {CHARACTERS["female"]}: {results["female"]}/{POKEMON.pokedex.females}{region_msg}

Spawnables: {spawnables_have}/{spawnables_total} ({spawnables_per}%)
    A: {spawnables_a_have}/{spawnables_a_total} ({spawnables_a_per}%) {missing_a_string}
    B: {spawnables_b_have}/{spawnables_b_total} ({spawnables_b_per}%) {missing_b_string}
    C: {spawnables_c_have}/{spawnables_c_total} ({spawnables_c_per}%) {missing_c_string}

Tradables: {tradable_total}
    A: {results["tradeA"]}
    B: {results["tradeB"]}
    C: {results["tradeC"]}

Inventory: {cash}$ {coins} Battle Coins
    pokeball: {pokeball}
    premierball: {premierball}
    greatball: {greatball}
    ultraball: {ultraball}
    other: {otherball}

Battles:
    Wins: {battle_stats['wins']}/{battle_stats['battles']}
    Exp: {battle_stats['exp']}
    $: {battle_stats['cash']}
        """

        POKEMON.discord.post(DISCORD_STATS, discord_msg)

    def check_bag_pokemon(self):
        for pokemon in POKEMON.computer.pokemon:
            pokemon_obj = self.get_pokemon_stats(pokemon["pokedexId"])
            updated = False

            if pokemon["name"] != pokemon_obj.name:
                POKEMON.pokedex.pokemon_stats[str(pokemon["pokedexId"])]["name"] = pokemon["name"]
                updated = True

            if pokemon["order"] != pokemon_obj.order:
                POKEMON.pokedex.pokemon_stats[str(pokemon["pokedexId"])]["order"] = pokemon["order"]
                updated = True

            if pokemon_obj.evolve_to is None:
                self.update_evolutions(pokemon["id"], pokemon["pokedexId"])
                log("yellow", f"Updated evolutions for{pokemon['pokedexId']}")
                sleep(1)
            elif updated:
                POKEMON.pokedex.save_pokedex()

    def check_finish_pokedex(self):
        must_catch = []
        can_evolve = []
        missing_pre_evo = []
        stones = {}
        required_pokemon = {}
        for i in range(1, POKEMON.pokedex.total + 1):
            pokemon = self.get_pokemon_stats(i)

            if pokemon.is_starter or pokemon.is_legendary or pokemon.is_non_spawnable or POKEMON.pokedex.have(pokemon):
                continue

            if len(pokemon.evolve_from) == 0:
                must_catch.append(pokemon.name)
                continue

            have_pre_to_evolve = False
            for pre_evolve in pokemon.evolve_from:
                pre_pokemon = self.get_pokemon_stats(pre_evolve)
                hits = POKEMON.computer.get_pokemon(pre_pokemon)
                if len(hits) > required_pokemon.get(pre_pokemon, 0):
                    required_pokemon[pre_pokemon] = required_pokemon.get(pre_pokemon, 0) + 1
                    have_pre_to_evolve = True
                    for evolve_into in pre_pokemon.evolve_to:
                        if evolve_into == str(pokemon.pokedex_id):
                            for stone in pre_pokemon.evolve_to[evolve_into]["stones"]:
                                stones[stone["stone"]] = stones.get(stone["stone"], 0) + stone["amount"]
                            break
                    break

            if have_pre_to_evolve:
                can_evolve.append(pokemon.name)
            else:
                missing_pre_evo.append(pokemon.name)

        discord_msg = "Pokedex Progress:"
        if len(must_catch) > 0:
            discord_msg += f"\n    Must Catch: {len(must_catch)} (" + ",".join(must_catch) + ")"
        if len(missing_pre_evo) > 0:
            discord_msg += f"\n    Missing Evo: {len(missing_pre_evo)} (" + ",".join(missing_pre_evo) + ")"
        if len(can_evolve) > 0:
            discord_msg += f"\n    Can Evolve: {len(can_evolve)} (" + ",".join(can_evolve) + ")"

        got_enough_stones = True
        if len(stones.keys()) > 0:
            discord_msg += "\n    Stone Requirements:"
            for stone in sorted(stones.keys()):
                stone_need = stones[stone]
                inv_stone = POKEMON.inventory.get_item(stone + " stone")
                stone_have = 0 if inv_stone is None else inv_stone["amount"]
                discord_msg += f"\n        {stone}: {stone_have}/{stone_need}"
                if stone_have >= stone_need:
                    discord_msg += " :white_check_mark:"
                else:
                    got_enough_stones = False

        if len(must_catch) == 0 and len(missing_pre_evo) == 0 and got_enough_stones:
            discord_msg += "\n\n    POKEDEX CAN BE COMPLETED!"

        POKEMON.discord.post(DISCORD_STATS, discord_msg)
