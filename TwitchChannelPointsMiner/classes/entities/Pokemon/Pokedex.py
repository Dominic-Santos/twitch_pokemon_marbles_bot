import json

from .Pokemon import Pokemon

POKEDEX_FILE = "pokemon_pokedex.json"
POKEMOVE_FILE = "pokemon_moves.json"

STARTER_POKEMON = ["Bulbasaur", "Ivysaur", "Venusaur", "Charmander", "Charmeleon", "Charizard", "Squirtle", "Wartortle", "Blastoise", "Chikorita", "Bayleef", "Meganium", "Cyndaquil", "Quilava", "Typhlosion", "Totodile", "Croconaw", "Feraligatr", "Treecko", "Grovyle", "Sceptile", "Torchic", "Combusken", "Blaziken", "Mudkip", "Marshtomp", "Swampert", "Turtwig", "Grotle", "Torterra", "Chimchar", "Monferno", "Infernape", "Piplup", "Prinplup", "Empoleon", "Snivy", "Servine", "Serperior", "Tepig", "Pignite", "Emboar", "Oshawott", "Dewott", "Samurott", "Chespin", "Quilladin", "Chesnaught", "Fennekin", "Braixen", "Delphox", "Froakie", "Frogadier", "Greninja", "Rowlet", "Dartrix", "Decidueye", "Litten", "Torracat", "Incineroar", "Popplio", "Brionne", "Primarina", "Grookey", "Thwackey", "Rillaboom", "Scorbunny", "Raboot", "Cinderace", "Sobble", "Drizzile", "Inteleon"]
LEGENDARY_POKEMON = ["Articuno", "Zapdos", "Moltres", "Mewtwo", "Mew", "Raikou", "Entei", "Suicune", "Lugia", "Ho-Oh", "Celebi", "Regirock", "Regice", "Registeel", "Latias", "Latios", "Kyogre", "Groudon", "Rayquaza", "Jirachi", "Deoxys", "Uxie", "Mesprit", "Azelf", "Dialga", "Palkia", "Heatran", "Regigigas", "Giratina", "Cresselia", "Phione", "Manaphy", "Darkrai", "Shaymin", "Arceus", "Victini", "Cobalion", "Terrakion", "Virizion", "Tornadus", "Thundurus", "Reshiram", "Zekrom", "Landorus", "Kyurem", "Keldeo", "Meloetta", "Genesect", "Xerneas", "Yveltal", "Zygarde", "Diancie", "Hoopa", "Volcanion", "Type: Null", "Silvally", "Tapu Koko", "Tapu Lele", "Tapu Bulu", "Tapu Fini", "Cosmog", "Cosmoem", "Solgaleo", "Lunala", "Nihilego", "Buzzwole", "Pheromosa", "Xurkitree", "Celesteela", "Kartana", "Guzzlord", "Necrozma", "Magearna", "Marshadow", "Poipole", "Naganadel", "Stakataka", "Blacephalon", "Zeraora", "Meltan", "Melmetal", "Zacian", "Zamazenta", "Eternatus", "Kubfu", "Urshifu", "Zarude", "Regieleki", "Regidrago", "Glastrier", "Spectrier", "Calyrex", "Wyrdeer", "Kleavor", "Ursaluna", "Basculegion", "Sneasler", "Overqwil", "Type: Null"]
FISH_POKEMON = ["Alomomola", "Angerphish", "Arctovish", "Arrokuda", "Barboach", "Barbubble", "Barraskewda", "Basculegion", "Basculin", "Blaufisch", "Bruxish", "Bubbayou", "Carvanha", "Chinchou", "Dragalge", "Eelektrik", "Elektross", "Feebas", "Finneon", "Goldeen", "Gorebyss", "Gyarados", "Horsea", "Huntail", "Kingdra", "Kyogre", "Lanturn", "Lumineon", "Luvdisc", "Magikarp", "Mantine", "Mantyke", "Milotic", "Mudkip", "Overqwil", "Qwilfish", "Relicanth", "Remoraid", "Seadra", "Seaking", "Sharpedo", "Skrelp", "Stunfisk", "Tynamo", "Wailmer", "Wailord", "Whiscash", "Wishiwashi", "Wooper", "Dracovish", "Clauncher", "Clawitzer"]
CAT_POKEMON = [52, 53, 134, 135, 136, 196, 215, 300, 301, 335, 403, 404, 405, 431, 432, 461, 470, 471, 509, 510, 667, 668, 677, 678, 700, 725, 726, 727, 807, 863, 903, 10025, 10107, 10108, 10387, 10388, 10399, 10400, 10401, 10445, 10471, 10493, 10540, 86325]
DOG_POKEMON = [37, 38, 58, 59, 133, 135, 197, 209, 210, 228, 229, 235, 243, 244, 261, 262, 309, 310, 359, 447, 448, 492, 506, 507, 508, 570, 571, 676, 744, 745, 773, 827, 828, 835, 836, 888, 889, 10006, 10048, 10055, 10057, 10059, 10116, 10117, 10320, 10321, 10341, 10342, 10343, 10344, 10345, 10346, 10347, 10348, 10349, 10372, 10472, 10473, 10474, 10475, 10476, 10477, 10478, 10479, 10480, 10481, 10482, 10483, 10484, 10485, 10486, 10487, 10488, 10548, 10549, 86316, 86319, 86322, 86323, 100009]
FEMALE_POKEMON = [10025, 86320, 10143, 10144, 10262, 10284, 10285, 10286, 10287, 10288, 10292, 10295, 10302, 10309, 10316, 10319, 10325, 10340, 10350, 10352, 10359, 10360, 10361, 10362, 10365, 10368, 10370, 10372, 10373, 10375, 10378, 10379, 10381, 10382, 10384, 10385, 10387, 10388, 10391, 10392, 10396, 10404, 10418, 10422, 10423, 10424, 10427, 10429, 10438, 10441, 10442, 10445, 10446, 10449, 10451, 10452, 10453, 10454, 10455, 10456, 10467, 10468, 10470, 10471, 10540, 10543, 10544, 10545, 10553, 10331, 10369, 10505, 10303]

REGION_PREFIX = {
    "Galarian": "Gal",
    "Hisuian": "His",
    "Alolan": "Alo",
    "Sinister": "Sin",
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
        self.pokemon_stats = {}
        self.pokemon_moves = {}
        self._total = 904
        self.load_pokedex()
        self.load_moves()
        self.count_totals()

    def count_totals(self):
        self._total_sin = len([x for x in self.pokemon_stats if self.pokemon_stats[x]["name"].lower().startswith("sin ")])
        self._total_gal = len([x for x in self.pokemon_stats if self.pokemon_stats[x]["name"].lower().startswith("gal ")])
        self._total_his = len([x for x in self.pokemon_stats if self.pokemon_stats[x]["name"].lower().startswith("his ")])
        self._total_alo = len([x for x in self.pokemon_stats if self.pokemon_stats[x]["name"].lower().startswith("alo ")])

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
            if pokemon["id"] < 10000:
                pokename = self._clean_pokedex_name(pokemon["name"])
                if pokename is not None:
                    self.pokemon[pokename] = pokemon["c"]
        self._total = dex["totalPkm"]

    def set_tier(self, pokemon, tier):
        poke_name = self._get_pokemon_name(pokemon)
        for t in self.tiers:
            if poke_name in self.tiers[t]:
                self.tiers[t].remove(poke_name)

        self.tiers[tier].append(poke_name)
        self.save_tiers()

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

    def _get_pokemon_id(self, pokemon):
        if isinstance(pokemon, Pokemon) is False:
            for poke_id in self.pokemon_stats.keys():
                pokeobj = self.stats(poke_id)
                if pokeobj.name == pokemon:
                    pokemon = pokeobj
                    break

        if isinstance(pokemon, Pokemon) is False:
            return 0

        return pokemon.pokedex_id

    def have(self, pokemon):
        poke_name = self._get_pokemon_name(pokemon)
        if poke_name is None:
            return None
        return self.pokemon.get(poke_name, None)

    def need(self, pokemon):
        return self.have(pokemon) is False

    def starter(self, pokemon):
        poke_name = self._get_pokemon_name(pokemon)
        return poke_name in STARTER_POKEMON

    def legendary(self, pokemon):
        poke_name = self._get_pokemon_name(pokemon)
        return poke_name in LEGENDARY_POKEMON

    def fish(self, pokemon):
        poke_name = self._get_pokemon_name(pokemon)
        return poke_name in FISH_POKEMON

    def cat(self, pokemon):
        poke_id = self._get_pokemon_id(pokemon)
        return poke_id in CAT_POKEMON

    def dog(self, pokemon):
        poke_id = self._get_pokemon_id(pokemon)
        return poke_id in DOG_POKEMON

    def female(self, pokemon):
        poke_id = self._get_pokemon_id(pokemon)
        return poke_id in FEMALE_POKEMON

    def baby(self, pokemon):
        poke_id = self._get_pokemon_id(pokemon)
        if poke_id is not None:
            pokemon = self.stats(poke_id)
            if pokemon is not None and pokemon.evolve_to is not None:
                for evolution_id in pokemon.evolve_to.keys():
                    evolution = self.stats(evolution_id)
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

    def stats(self, pokemon_id):
        poke_id = str(pokemon_id)
        if poke_id not in self.pokemon_stats:
            return None

        poke = Pokemon(self.pokemon_stats[poke_id])

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
        return self.total - self.starters - self.legendaries

    @property
    def starters(self):
        return len(STARTER_POKEMON)

    @property
    def legendaries(self):
        return len(LEGENDARY_POKEMON)

    @property
    def females(self):
        return len(FEMALE_POKEMON)

    @property
    def fishes(self):
        return len(FISH_POKEMON)

    @property
    def prefixes(self):
        return REGION_PREFIX

    @property
    def galarian(self):
        return self._total_gal

    @property
    def hisuian(self):
        return self._total_his

    @property
    def alolan(self):
        return self._total_alo

    @property
    def sinister(self):
        return self._total_sin
