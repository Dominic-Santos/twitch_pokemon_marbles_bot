import json

from .Pokemon import Pokemon

POKEDEX_FILE = "pokemon_pokedex.json"
POKEMOVE_FILE = "pokemon_moves.json"

STARTER_POKEMON = ["Bulbasaur", "Ivysaur", "Venusaur", "Charmander", "Charmeleon", "Charizard", "Squirtle", "Wartortle", "Blastoise", "Chikorita", "Bayleef", "Meganium", "Cyndaquil", "Quilava", "Typhlosion", "Totodile", "Croconaw", "Feraligatr", "Treecko", "Grovyle", "Sceptile", "Torchic", "Combusken", "Blaziken", "Mudkip", "Marshtomp", "Swampert", "Turtwig", "Grotle", "Torterra", "Chimchar", "Monferno", "Infernape", "Piplup", "Prinplup", "Empoleon", "Snivy", "Servine", "Serperior", "Tepig", "Pignite", "Emboar", "Oshawott", "Dewott", "Samurott", "Chespin", "Quilladin", "Chesnaught", "Fennekin", "Braixen", "Delphox", "Froakie", "Frogadier", "Greninja", "Rowlet", "Dartrix", "Decidueye", "Litten", "Torracat", "Incineroar", "Popplio", "Brionne", "Primarina", "Grookey", "Thwackey", "Rillaboom", "Scorbunny", "Raboot", "Cinderace", "Sobble", "Drizzile", "Inteleon"]
LEGENDARY_POKEMON = ["Articuno", "Zapdos", "Moltres", "Mewtwo", "Mew", "Raikou", "Entei", "Suicune", "Lugia", "Ho-Oh", "Celebi", "Regirock", "Regice", "Registeel", "Latias", "Latios", "Kyogre", "Groudon", "Rayquaza", "Jirachi", "Deoxys", "Uxie", "Mesprit", "Azelf", "Dialga", "Palkia", "Heatran", "Regigigas", "Giratina", "Cresselia", "Phione", "Manaphy", "Darkrai", "Shaymin", "Arceus", "Victini", "Cobalion", "Terrakion", "Virizion", "Tornadus", "Thundurus", "Reshiram", "Zekrom", "Landorus", "Kyurem", "Keldeo", "Meloetta", "Genesect", "Xerneas", "Yveltal", "Zygarde", "Diancie", "Hoopa", "Volcanion", "Type: Null", "Silvally", "Tapu Koko", "Tapu Lele", "Tapu Bulu", "Tapu Fini", "Cosmog", "Cosmoem", "Solgaleo", "Lunala", "Nihilego", "Buzzwole", "Pheromosa", "Xurkitree", "Celesteela", "Kartana", "Guzzlord", "Necrozma", "Magearna", "Marshadow", "Poipole", "Naganadel", "Stakataka", "Blacephalon", "Zeraora", "Meltan", "Melmetal", "Zacian", "Zamazenta", "Eternatus", "Kubfu", "Urshifu", "Zarude", "Regieleki", "Regidrago", "Glastrier", "Spectrier", "Calyrex", "Wyrdeer", "Kleavor", "Ursaluna", "Basculegion", "Sneasler", "Overqwil", "Type: Null"]
FISH_POKEMON = ["Alomomola", "Angerphish", "Arctovish", "Arrokuda", "Barboach", "Barbubble", "Barraskewda", "Basculegion", "Basculin", "Blaufisch", "Bruxish", "Bubbayou", "Carvanha", "Chinchou", "Dragalge", "Eelektrik", "Elektross", "Feebas", "Finneon", "Goldeen", "Gorebyss", "Gyarados", "Horsea", "Huntail", "Kingdra", "Kyogre", "Lanturn", "Lumineon", "Luvdisc", "Magikarp", "Mantine", "Mantyke", "Milotic", "Mudkip", "Overqwil", "Qwilfish", "Relicanth", "Remoraid", "Seadra", "Seaking", "Sharpedo", "Skrelp", "Stunfisk", "Tynamo", "Wailmer", "Wailord", "Whiscash", "Wishiwashi", "Wooper", "Dracovish", "Clauncher", "Clawitzer"]
FEMALE_POKEMON = [10025, 86320, 10143, 10144, 10262, 10284, 10285, 10286, 10287, 10288, 10292, 10295, 10302, 10309, 10316, 10319, 10325, 10340, 10350, 10352, 10359, 10360, 10361, 10362, 10365, 10368, 10370, 10372, 10373, 10375, 10378, 10379, 10381, 10382, 10384, 10385, 10387, 10388, 10391, 10392, 10396, 10404, 10418, 10422, 10423, 10424, 10427, 10429, 10438, 10441, 10442, 10445, 10446, 10449, 10451, 10452, 10453, 10454, 10455, 10456, 10467, 10468, 10470, 10471, 10540, 10543, 10544, 10545, 10553, 10331, 10369, 10505]
THREE_EVOS = ["Bulbasaur", "Charmander", "Squirtle", "Caterpie", "Weedle", "Pidgey", "Pichu", "Nidoran-male", "Nidoran-female", "Cleffa", "Igglybuff", "Zubat", "Oddish", "Mankey", "Poliwag", "Abra", "Machop", "Bellsprout", "Geodude", "Magnemite", "Rhyhorn", "Happiny", "Horsea", "Mime Jr.", "Elekid", "Magby", "Porygon", "Dratini", "Chikorita", "Cyndaquil", "Totodile", "Togepi", "Mareep", "Azurill", "Hoppip", "Teddiursa", "Swinub", "Larvitar", "Treecko", "Torchic", "Mudkip", "Wurmple", "Lotad", "Seedot", "Ralts", "Slakoth", "Whismur", "Aron", "Budew", "Trapinch", "Duskull", "Spheal", "Bagon", "Beldum", "Turtwig", "Chimchar", "Piplup", "Starly", "Shinx", "Gible", "Snivey", "Tepig", "Oshawott", "Lillipup", "Pidove", "Roggenrola", "Timbur", "Tympole", "Sewaddle", "Venipede", "Sandile", "Gothita", "Solosis", "Vanillite", "Klink", "Tynamo", "Litwick", "Axew", "Pawniard", "Deino", "Chespin", "Fennekin", "Froakie", "Fletchling", "Scatterbug", "Flabébé", "Honedge", "Goomy", "Rowlet", "Litten", "Popplio", "Pipipek", "Grubbin", "Bounsweet", "Jangmo-o", "Cosmog", "Grookey", "Scorbunny", "Sobble", "Rookidee", "Blipbug", "Rolycoly", "Hatenna", "Impidimp", "Dreepy", "Sprigatito", "Fuecoco", "Quaxly", "Pawmi", "Smoliv", "Nacli", "Tinkatink", "Frigibax"]

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

    @staticmethod
    def _get_pokemon_id(pokemon):
        if isinstance(pokemon, Pokemon):
            return pokemon.pokedex_id
        return pokemon

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

    def female(self, pokemon):
        poke_id = self._get_pokemon_id(pokemon)
        return poke_id in FEMALE_POKEMON

    def baby(self, pokemon):
        poke_name = self._get_pokemon_name(pokemon)
        return poke_name in THREE_EVOS

    @staticmethod
    def remove_region(pokemon):
        poke_name = pokemon
        for prefix in REGION_PREFIX.values():
            poke_name = poke_name.replace(f"{prefix} ", "").strip()
        for prefix in REGION_PREFIX.keys():
            poke_name = poke_name.replace(f"{prefix} ", "").strip()
        return poke_name

    def stats(self, pokemon_id):
        if pokemon_id not in self.pokemon_stats:
            return None

        poke = Pokemon(self.pokemon_stats[pokemon_id])

        return poke

    def move(self, move_name):
        if move_name not in self.pokemon_moves:
            return None

        move = Move(move_name, self.pokemon_moves[move_name])

        return move

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
