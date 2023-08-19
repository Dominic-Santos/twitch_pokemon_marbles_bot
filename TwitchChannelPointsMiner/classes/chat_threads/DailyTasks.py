from datetime import datetime
from dateutil.parser import parse
from time import sleep
import traceback

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


def battle_summary(battle_date):
    battle_stats = get_battle_logs(battle_date)

    discord_msg = f"""Battle Summary - {battle_date}:
    Wins: {battle_stats['wins']}/{battle_stats['battles']}
    Exp: {battle_stats['exp']}
    $: {battle_stats['cash']}"""

    return discord_msg


def stats_computer(Pokemon, get_stats_func):
    allpokemon = Pokemon.computer.pokemon

    spawnables = {tier + suffix: [] for tier in ["S", "A", "B", "C"] for suffix in ["_have", "_dont_have"]}
    for i in range(1, Pokemon.pokedex.total + 1):
        pokemon = get_stats_func(i)

        if pokemon.is_starter or pokemon.is_legendary or pokemon.is_non_spawnable:
            continue

        if Pokemon.pokedex.have(pokemon):
            spawnables[pokemon.tier + "_have"].append(pokemon)
        else:
            spawnables[pokemon.tier + "_dont_have"].append(pokemon)

    for k in spawnables:
        if "dont" not in k:
            spawnables[k] = len(spawnables[k])

    spawnables["have"] = sum(y for x, y in spawnables.items() if "dont" not in x)

    spawnables_per = {}
    for tier in ["S", "A", "B", "C"]:
        total = Pokemon.pokedex.tier(tier)
        if total == 0:
            spawnables_per[tier] = 100
        else:
            spawnables_per[tier] = int(spawnables.get(tier + "_have", 0) * 10000.0 / total) / 100.0
    spawnables_per["total"] = int(spawnables["have"] * 10000.0 / Pokemon.pokedex.spawnables) / 100.0

    results = {
        "shiny": [],
        "starter": [],
        "female": [],
        "legendary": [],
        "non_spawnable": [],
        "bag_regular": [],
        "bag_special": [],
    }

    for tier in ["S", "A", "B", "C"]:
        results[f"trade{tier}"] = []

    regions = {shrt: lng for lng, shrt in Pokemon.pokedex.prefixes.items()}
    for region in regions.keys():
        results[region] = []

    for pokemon in allpokemon:
        if pokemon["isShiny"]:
            results["shiny"].append(pokemon)

        pokeobj = get_stats_func(pokemon["pokedexId"])
        if pokeobj is None:
            continue
        if pokeobj.is_starter:
            results["starter"].append(pokeobj.pokedex_id)
        if pokeobj.is_female:
            results["female"].append(pokeobj.pokedex_id)
        if pokeobj.is_legendary:
            results["legendary"].append(pokeobj.pokedex_id)
        if pokeobj.is_non_spawnable:
            results["non_spawnable"].append(pokeobj.pokedex_id)
        if pokeobj.pokedex_id <= Pokemon.pokedex.total:
            results["bag_regular"].append(pokeobj.pokedex_id)
        else:
            results["bag_special"].append(pokeobj.pokedex_id)

        if pokemon["nickname"] is not None and "trade" in pokemon["nickname"]:
            results[f"trade{pokeobj.tier}"].append(pokemon)

        if " " in pokemon["name"]:
            region = pokemon["name"].split(" ")[0]
            if region in regions:
                results[region].append(pokeobj.pokedex_id)

    for k in results.keys():
        if "trade" in k or k == "shiny":
            results[k] = len(results[k])
        else:
            results[k] = len(set(results[k]))

    results["trade_total"] = sum([results[k] for k in results.keys() if k.startswith("trade")])

    region_msg_list = []
    for region in regions:
        if results[region] > 0:
            region_msg_list.append((regions[region], results[region], getattr(Pokemon.pokedex, regions[region].lower())))

    region_msg = "".join([f"\n    {region}: {num}/{total}" for region, num, total in region_msg_list])

    cash = Pokemon.inventory.cash
    pokeball = Pokemon.inventory.balls.get("pokeball", 0)
    premierball = Pokemon.inventory.balls.get("premierball", 0)
    greatball = Pokemon.inventory.balls.get("greatball", 0)
    ultraball = Pokemon.inventory.balls.get("ultraball", 0)
    otherball = sum([value for key, value in Pokemon.inventory.balls.items() if key not in ["pokeball", "premierball", "greatball", "ultraball"]])

    if Pokemon.inventory.have_item("battle coin"):
        coins = Pokemon.inventory.get_item("battle coin")["amount"]
    else:
        coins = 0

    max_show_missing = 20
    missing_strings = []
    for tier in ["A", "B", "C"]:
        dont_haves = len(spawnables[tier + "_dont_have"])
        if dont_haves == 0:
            missing_strings.append("Done")
        elif dont_haves < max_show_missing:
            missing_strings.append("missing: " + ", ".join([pokemon.name for pokemon in spawnables[tier + "_dont_have"]]))

    tradable_msg = "".join(f"\n    {tier}: {results['trade' + tier]}" for tier in ["S", "A", "B", "C"] if results["trade" + tier] > 0)

    msg = f"""Bag Summary:

Starters: {results["starter"]}
Legendary: {results["legendary"]}
Non-Spawnables: {results["non_spawnable"]}/{Pokemon.pokedex.non_spawnables}
Shiny: {results["shiny"]}

Normal Version: {results["bag_regular"]}/{Pokemon.pokedex.total}
Alt Version: {results["bag_special"]}
    {CHARACTERS["female"]}: {results["female"]}/{Pokemon.pokedex.females}{region_msg}

Spawnables: {spawnables['have']}/{Pokemon.pokedex.spawnables} ({spawnables_per['total']}%)
    A: {spawnables['A_have']}/{Pokemon.pokedex.tier('A')} ({spawnables_per['A']}%) {missing_strings[0]}
    B: {spawnables['B_have']}/{Pokemon.pokedex.tier('B')} ({spawnables_per['B']}%) {missing_strings[1]}
    C: {spawnables['C_have']}/{Pokemon.pokedex.tier('C')} ({spawnables_per['C']}%) {missing_strings[2]}

Tradables: {results["trade_total"]}{tradable_msg}

Inventory: {cash}$ {coins} Battle Coins
    pokeball: {pokeball}
    premierball: {premierball}
    greatball: {greatball}
    ultraball: {ultraball}
    other: {otherball}"""

    return msg


def check_finish_pokedex(Pokemon, get_stats_func):
    must_catch = []
    can_evolve = []
    missing_pre_evo = []
    stones = {}
    required_pokemon = {}
    for i in range(1, Pokemon.pokedex.total + 1):
        pokemon = get_stats_func(i)

        if pokemon is None:
            continue

        if pokemon.is_starter or pokemon.is_legendary or pokemon.is_non_spawnable or Pokemon.pokedex.have(pokemon):
            continue

        if len(pokemon.evolve_from) == 0:
            must_catch.append(pokemon.name)
            continue

        have_pre_to_evolve = False
        for pre_evolve in pokemon.evolve_from:
            pre_pokemon = get_stats_func(pre_evolve)
            hits = Pokemon.computer.get_pokemon(pre_pokemon)
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
            inv_stone = Pokemon.inventory.get_item(stone + " stone")
            stone_have = 0 if inv_stone is None else inv_stone["amount"]
            discord_msg += f"\n        {stone}: {stone_have}/{stone_need}"
            if stone_have >= stone_need:
                discord_msg += " :white_check_mark:"
            else:
                got_enough_stones = False

    if len(must_catch) == 0 and len(missing_pre_evo) == 0 and got_enough_stones:
        discord_msg += "\n\n    POKEDEX CAN BE COMPLETED!"

    return discord_msg


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
        stats_date = previous_date if previous_date is not None else current_date
        self.stats_computer()
        self.battle_summary(stats_date)
        self.check_bag_pokemon()
        self.check_finish_pokedex()

    def stats_computer(self):
        all_pokemon = self.pokemon_api.get_all_pokemon()
        POKEMON.sync_computer(all_pokemon)

        dex = self.pokemon_api.get_pokedex()
        POKEMON.sync_pokedex(dex)

        inv = self.pokemon_api.get_inventory()
        POKEMON.sync_inventory(inv)

        discord_msg = stats_computer(POKEMON, self.get_pokemon_stats)

        POKEMON.discord.post(DISCORD_STATS, discord_msg)

    def battle_summary(self, battle_date):
        discord_msg = battle_summary(battle_date)

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
        discord_msg = check_finish_pokedex(POKEMON, self.get_pokemon_stats)

        POKEMON.discord.post(DISCORD_STATS, discord_msg)
