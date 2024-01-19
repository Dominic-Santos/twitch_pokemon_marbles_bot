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
