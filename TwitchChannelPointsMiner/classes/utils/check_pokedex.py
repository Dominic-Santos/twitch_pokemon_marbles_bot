from ..Utils import DISCORD_STATS


def discord_update_pokedex(Pokemon, pokemon_api, get_pokemon_stats):
    dex = pokemon_api.get_pokedex()
    Pokemon.sync_pokedex(dex)

    discord_msg = check_pokedex(Pokemon, get_pokemon_stats)

    Pokemon.discord.post(DISCORD_STATS, discord_msg)


def check_pokedex(Pokemon, get_stats_func):
    spawnables = {tier + suffix: [] for tier in ["S", "A", "B", "C"] for suffix in ["_have", "_dont_have"]}
    non_spawnables = {tier + suffix: [] for tier in ["S", "A", "B", "C"] for suffix in ["_have", "_dont_have"]}
    for i in range(1, Pokemon.pokedex.total + 1):
        pokemon = get_stats_func(i)

        if pokemon.is_starter or pokemon.is_legendary or pokemon.is_non_spawnable:
            to_use = non_spawnables
        else:
            to_use = spawnables

        sufix = "_have" if Pokemon.pokedex.have(pokemon) else "_dont_have"
        to_use[pokemon.tier + sufix].append(pokemon)

    for k in spawnables:
        if "dont" not in k:
            spawnables[k] = len(spawnables[k])

    spawnables["have"] = sum(y for x, y in spawnables.items() if "dont" not in x)

    spawnables_per = {}
    for tier in ["S", "A", "B", "C"]:
        total = Pokemon.pokedex.spawnable_tier(tier)
        if total == 0:
            spawnables_per[tier] = 100
        else:
            spawnables_per[tier] = int(spawnables.get(tier + "_have", 0) * 10000.0 / total) / 100.0
    spawnables_per["total"] = int(spawnables["have"] * 10000.0 / Pokemon.pokedex.spawnables) / 100.0

    max_show_missing = 20
    missing_strings = []
    for tier in ["A", "B", "C"]:
        dont_haves = len(spawnables[tier + "_dont_have"])
        mstring = ""
        if dont_haves == 0:
            mstring = "Done"
        elif dont_haves < max_show_missing:
            mstring = "missing: " + ", ".join([pokemon.name for pokemon in spawnables[tier + "_dont_have"]])

        missing_strings.append(mstring)

    non_spawnables_have = sum([len(non_spawnables[tier + "_have"]) for tier in ["S", "A", "B", "C"]])
    total_have = spawnables["have"] + non_spawnables_have
    total_per = int(total_have * 10000.0 / Pokemon.pokedex.total) / 100.0

    alts_total = 0
    alts_caught = 0
    for pokemon_id in Pokemon.pokedex.pokemon_ids:
        if pokemon_id <= Pokemon.pokedex.total:
            continue
        alts_total += 1
        if Pokemon.pokedex.pokemon_ids[pokemon_id]:
            alts_caught += 1

    alts_per = int(alts_caught * 10000.0 / alts_total) / 100.0

    msg = f"""Pokedex: {total_have}/{Pokemon.pokedex.total} ({total_per}%)
Alt Pokedex: {alts_caught}/{alts_total} ({alts_per}%)

Spawnable Pokedex: {spawnables['have']}/{Pokemon.pokedex.spawnables} ({spawnables_per['total']}%)
    A: {spawnables['A_have']}/{Pokemon.pokedex.spawnable_tier('A')} ({spawnables_per['A']}%) {missing_strings[0]}
    B: {spawnables['B_have']}/{Pokemon.pokedex.spawnable_tier('B')} ({spawnables_per['B']}%) {missing_strings[1]}
    C: {spawnables['C_have']}/{Pokemon.pokedex.spawnable_tier('C')} ({spawnables_per['C']}%) {missing_strings[2]}"""

    return msg
