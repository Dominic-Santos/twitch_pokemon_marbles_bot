from ..ChatUtils import CHARACTERS


def stats_computer(Pokemon, get_stats_func):
    allpokemon = Pokemon.computer.pokemon

    results = {
        "shiny": [],
        "starter": [],
        "female": [],
        "legendary": [],
        "non_spawnable": [],
        "bag_regular": [],
        "bag_special": [],
    }
    value_total = 0
    value_trade = 0
    level_100s = 0

    for tier in ["S", "A", "B", "C"]:
        results[f"trade{tier}"] = []

    regions = {shrt: lng for lng, shrt in Pokemon.pokedex.prefixes.items()}
    for region in regions.keys():
        results[region] = []

    for pokemon in allpokemon:
        pokeobj = get_stats_func(pokemon["pokedexId"])
        if pokeobj is None:
            continue

        if pokemon["isShiny"]:
            results["shiny"].append(pokemon)

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

        value_total += pokemon["sellPrice"]

        if pokemon["nickname"] is not None and "trade" in pokemon["nickname"]:
            results[f"trade{pokeobj.tier}"].append(pokemon)
            value_trade += pokemon["sellPrice"]

        if " " in pokemon["name"]:
            region = pokemon["name"].split(" ")[0]
            if region in regions:
                results[region].append(pokeobj.pokedex_id)

        if pokemon["lvl"] >= 100:
            level_100s += 1


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

    tradable_msg = "".join(f"\n    {tier}: {results['trade' + tier]}" for tier in ["S", "A", "B", "C"] if results["trade" + tier] > 0)
    msg = f"""Bag Summary:

Starters: {results["starter"]}
Legendary: {results["legendary"]}
Non-Spawnables: {results["non_spawnable"]}
Shiny: {results["shiny"]}
Level 100: {level_100s}

Normal Version: {results["bag_regular"]}/{Pokemon.pokedex.total}
Alt Version: {results["bag_special"]}
    {CHARACTERS["female"]}: {results["female"]}/{Pokemon.pokedex.females}{region_msg}

Tradables: {results["trade_total"]}{tradable_msg}

Inventory: {cash}$ {coins} Battle Coins
    pokeball: {pokeball}
    premierball: {premierball}
    greatball: {greatball}
    ultraball: {ultraball}
    other: {otherball}

Pokemon Value:
    total: {value_total}$
    trade: {value_trade}$
    """

    return msg
