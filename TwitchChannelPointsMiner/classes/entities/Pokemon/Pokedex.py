import json

from .Pokemon import Pokemon

POKEDEX_FILE = "pokemon_pokedex.json"
POKEMOVE_FILE = "pokemon_moves.json"

STARTER_POKEMON = [y for x in (1, 152, 252, 387, 495, 650, 722, 810, 906) for y in range(x, x + 9)]
LEGENDARY_POKEMON = [z for x, y in ((144, 3), (150, 2), (243, 3), (249, 3), (377, 10), (480, 15), (638, 12), (716, 6), (772, 2), (785, 25), (888, 11)) for z in range(x, x + y)]
NON_SPAWNABLE_POKEMON = [899, 900, 901, 902, 903, 904]
FISH_POKEMON = [116, 117, 118, 119, 129, 130, 170, 171, 194, 211, 223, 226, 230, 258, 318, 319, 320, 321, 339, 340, 349, 350, 367, 368, 369, 370, 382, 456, 457, 458, 550, 594, 602, 603, 604, 618, 690, 691, 692, 693, 746, 779, 846, 847, 882, 883, 902, 904]
CAT_POKEMON = [52, 53, 134, 135, 136, 196, 215, 300, 301, 335, 403, 404, 405, 431, 432, 461, 470, 471, 509, 510, 667, 668, 677, 678, 700, 725, 726, 727, 807, 863, 903]
DOG_POKEMON = [37, 38, 58, 59, 133, 135, 197, 209, 210, 228, 229, 235, 243, 244, 261, 262, 309, 310, 359, 447, 448, 492, 506, 507, 508, 570, 571, 676, 744, 745, 773, 827, 828, 835, 836, 888, 889]
FEMALE_POKEMON = [10025, 86320, 10143, 10144, 10262, 10284, 10285, 10286, 10287, 10288, 10292, 10295, 10302, 10309, 10316, 10319, 10325, 10340, 10350, 10352, 10359, 10360, 10361, 10362, 10365, 10368, 10370, 10372, 10373, 10375, 10378, 10379, 10381, 10382, 10384, 10385, 10387, 10388, 10391, 10392, 10396, 10404, 10418, 10422, 10423, 10424, 10427, 10429, 10438, 10441, 10442, 10445, 10446, 10449, 10451, 10452, 10453, 10454, 10455, 10456, 10467, 10468, 10470, 10471, 10540, 10543, 10544, 10545, 10553, 10331, 10369, 10505, 10303]
POKEMON_TYPES = ["Normal", "Fighting", "Flying", "Poison", "Ground", "Rock", "Bug", "Ghost", "Steel", "Fire", "Water", "Grass", "Electric", "Psychic", "Ice", "Dragon", "Dark", "Fairy"]

REGION_PREFIX = {
    "Galarian": "Gal",
    "Hisuian": "His",
    "Alolan": "Alo",
    "Sinister": "Sin",
    "PCG": "PCG"
}


class Move(object):
    def __init__(self, move_id, data):
        self.move_id = move_id
        self.name = data.get("name", "")
        self.damage_class = data.get("damage_class", "")
        self.stat_chance = data.get("stat_chance", 0)
        self.effect_chance = data.get("effect_chance", 0)
        self.priority = data.get("priority", 0)
        self.description = data.get("description", "")
        self.power = data.get("power", 0)
        self.pp = data.get("pp", 0)
        self.accuracy = data.get("accuracy", 100)
        self.move_type = data.get("type", "none").title()


class Pokedex(object):
    def __init__(self):
        self.pokemon = {}
        self.pokemon_ids = {}
        self.pokemon_stats = {}
        self.pokemon_moves = {}
        self._total = 904
        self.load_pokedex()
        self.load_moves()
        self.count_totals()

    def count_totals(self):
        regions = [x.lower() for x in REGION_PREFIX.values()]

        self._tiers = {x: 0 for x in ["S", "A", "B", "C"]}
        self._spawnable_tiers = {x: 0 for x in ["S", "A", "B", "C"]}
        self._alts = 0
        self._total_regions = {x: 0 for x in regions}
        self._starters = 0
        self._legendaries = 0
        self._spawnables = 0

        for poke_id in self.pokemon_stats:
            poke = self.stats(poke_id)

            if poke.order == 0:
                # not confirmed to be real pokemon yet
                continue

            if poke.pokedex_id > self._total:
                self._alts += 1
            else:
                self._tiers[poke.tier] += 1
                if poke.is_starter:
                    self._starters += 1
                elif poke.is_legendary:
                    self._legendaries += 1
                elif poke.is_non_spawnable is False:
                    self._spawnables += 1
                    self._spawnable_tiers[poke.tier] += 1
            if " " in poke.name:
                region = poke.name.lower().split(" ")[0]
                if region in regions:
                    self._total_regions[region] += 1

    def load_pokedex(self):
        try:
            with open(POKEDEX_FILE, "r", encoding="utf-8") as f:
                self.pokemon_stats = json.load(f)
        except Exception as e:
            print(e)
            self.pokemon_stats = {}

    def save_pokedex(self):
        with open(POKEDEX_FILE, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.pokemon_stats, indent=4))

    def load_moves(self):
        try:
            with open(POKEMOVE_FILE, "r", encoding="utf-8") as f:
                self.pokemon_moves = json.load(f)
        except Exception as e:
            print(e)
            self.pokemon_moves = {}

    def save_moves(self):
        with open(POKEMOVE_FILE, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.pokemon_moves, indent=4))

    def set(self, dex):
        for pokemon in dex["dex"]:
            if pokemon["id"] <= dex["totalPkm"]:
                pokename = self._clean_pokedex_name(pokemon["name"])
                if pokename is not None:
                    self.pokemon[pokename] = pokemon["c"]
            self.pokemon_ids[pokemon["id"]] = pokemon["c"]
        self._total = dex["totalPkm"]

    def set_tier(self, pokemon, tier):
        poke_name = self._get_pokemon_name(pokemon)
        for t in self.tiers:
            if poke_name in self.tiers[t]:
                self.tiers[t].remove(poke_name)

        self.tiers[tier].append(poke_name)
        self.save_tiers()

    def tier(self, t):
        return self._tiers.get(t, 0)

    def spawnable_tier(self, t):
        return self._spawnable_tiers.get(t, 0)

    def _check_valid(self, pokemon):
        for k in self.tiers.keys():
            if pokemon in self.tiers[k]:
                return True
        return False

    def _clean_pokedex_name(self, pokemon):
        new_name = pokemon.replace("’", "").replace("'", "")

        if new_name.startswith("Aegislash"):
            return "Aegislash"

        if new_name.startswith("Nidoran"):
            new_name = "Nidoran-{sex}".format(sex="male" if "♂" in new_name else "female")
            return new_name

        for split_char in ["("]:
            new_name = new_name.split(split_char)[0].strip()

        return new_name

    def _get_pokemon_name(self, pokemon):
        if isinstance(pokemon, Pokemon):
            pokename = pokemon.name
        else:
            pokename = pokemon

        pokename = self.remove_region(pokename)

        pokename = self._clean_pokedex_name(pokename)

        return pokename

    def _get_pokemon_id(self, pokemon: Pokemon):
        if pokemon.order != 0:
            return pokemon.order
        return pokemon.pokedex_id

    def have_alt(self, pokemon: Pokemon):
        return self.pokemon_ids.get(pokemon.pokedex_id, True)

    def need_alt(self, pokemon):
        return self.have_alt(pokemon) is False

    def have(self, pokemon: Pokemon):
        pokedex_id = self._get_pokemon_id(pokemon)

        # check by id if not alt
        if pokedex_id <= self._total:
            result = self.pokemon_ids.get(pokedex_id, None)
            if result is not None:
                return result

        # try to get by name instead
        poke_name = self._get_pokemon_name(pokemon)

        if poke_name is not None:
            result = self.pokemon.get(poke_name, None)

        return None

    def need(self, pokemon):
        return self.have(pokemon) is False

    def starter(self, pokemon):
        poke_id = self._get_pokemon_id(pokemon)
        return poke_id in STARTER_POKEMON

    def legendary(self, pokemon):
        poke_id = self._get_pokemon_id(pokemon)
        return poke_id in LEGENDARY_POKEMON

    def non_spawnable(self, pokemon):
        poke_id = self._get_pokemon_id(pokemon)
        return poke_id in NON_SPAWNABLE_POKEMON

    def fish(self, pokemon):
        poke_id = self._get_pokemon_id(pokemon)
        return poke_id in FISH_POKEMON

    def cat(self, pokemon):
        poke_id = self._get_pokemon_id(pokemon)
        return poke_id in CAT_POKEMON

    def dog(self, pokemon):
        poke_id = self._get_pokemon_id(pokemon)
        return poke_id in DOG_POKEMON

    def female(self, pokemon):
        return pokemon.pokedex_id in FEMALE_POKEMON

    def baby(self, pokemon):
        poke_id = self._get_pokemon_id(pokemon)
        if poke_id is not None:
            pokemon = self._stats(poke_id)
            if pokemon is not None and pokemon.evolve_to is not None:
                for evolution_id in pokemon.evolve_to.keys():
                    evolution = self._stats(evolution_id)
                    if evolution is not None and evolution.evolve_to is not None:
                        if len(evolution.evolve_to.keys()) > 0:
                            return True
        return False

    @staticmethod
    def remove_region(pokemon):
        poke_name = pokemon
        for prefix in REGION_PREFIX.values():
            poke_name = poke_name.replace(f"{prefix} ", "").strip()
        for prefix in REGION_PREFIX.keys():
            poke_name = poke_name.replace(f"{prefix} ", "").strip()
        return poke_name

    def _stats(self, pokemon_id):
        poke_id = str(pokemon_id)
        if poke_id not in self.pokemon_stats:
            return None

        poke = Pokemon(self.pokemon_stats[poke_id])
        return poke

    def stats(self, pokemon_id):
        poke = self._stats(pokemon_id)
        if poke is None:
            return poke

        poke.is_fish = self.fish(poke)
        poke.is_cat = self.cat(poke)
        poke.is_dog = self.dog(poke)
        poke.is_baby = self.baby(poke)
        poke.is_legendary = self.legendary(poke)
        poke.is_starter = self.starter(poke)
        poke.is_female = self.female(poke)
        poke.is_non_spawnable = self.non_spawnable(poke)

        return poke

    def set_evolutions(self, pokemonid, data):
        pokemon_id = str(pokemonid)
        if pokemon_id in self.pokemon_stats:
            if "evolves_to" not in self.pokemon_stats[pokemon_id]:
                self.pokemon_stats[pokemon_id]["evolves_to"] = {}

            for other_id in data:
                level = 0
                stones = []
                for d in data[other_id]:
                    if d["req"].startswith("Level"):
                        level = int(d["req"].split(" ")[1])
                    elif d["req"].endswith("tone"):
                        stones.append({
                            "amount": int(d["req"].split("x")[0]),
                            "stone": d["req"].lower().split(" ")[1].replace("stone", " ").title()
                        })
                self.pokemon_stats[pokemon_id]["evolves_to"][other_id] = {"level": level, "stones": stones}
                if other_id in self.pokemon_stats and ("evolves_from" not in self.pokemon_stats[other_id] or pokemon_id not in self.pokemon_stats[other_id]["evolves_from"]):
                    self.pokemon_stats[other_id].setdefault("evolves_from", []).append(pokemon_id)

    def move(self, move_name):
        if move_name not in self.pokemon_moves:
            return None

        move = Move(move_name, self.pokemon_moves[move_name])

        return move

    def clean_name(self, pokemon):
        return self._get_pokemon_name(pokemon)

    @property
    def total(self):
        return self._total

    @property
    def spawnables(self):
        return self._spawnables

    @property
    def starters(self):
        return self._starters

    @property
    def legendaries(self):
        return self._legendaries

    @property
    def females(self):
        return len(FEMALE_POKEMON)

    @property
    def non_spawnables(self):
        return len(NON_SPAWNABLE_POKEMON)

    @property
    def prefixes(self):
        return REGION_PREFIX

    @property
    def galarian(self):
        return self._total_regions["gal"]

    @property
    def hisuian(self):
        return self._total_regions["his"]

    @property
    def alolan(self):
        return self._total_regions["alo"]

    @property
    def sinister(self):
        return self._total_regions["sin"]

    @property
    def pcg(self):
        return self._total_regions["pcg"]
