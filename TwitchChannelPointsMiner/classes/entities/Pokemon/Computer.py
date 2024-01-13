from .Pokemon import Pokemon
from .Utils import load_from_file, save_to_file

POKECOM_FILE = "pokemon_computer.json"


class Computer(object):
    def __init__(self):
        self.pokemon = []
        self.pokemon_data = {}
        self.load_computer()

    def load_computer(self):
        self.pokemon_data = load_from_file(POKECOM_FILE)

    def save_computer(self):
        save_to_file(POKECOM_FILE, self.pokemon_data)

    def set(self, computer):
        self.pokemon = computer["allPokemon"]

    def _have_by_id(self, pokemon_id):
        if pokemon_id != 0:
            for pokemon in self.pokemon:
                if pokemon["pokedexId"] == pokemon_id:
                    return True
        return False

    def _have_by_name(self, pokemon_name):
        for pokemon in self.pokemon:
            if pokemon["name"] == pokemon_name:
                return True
        return False

    def _get_by_id(self, pokemon_id):
        hits = []
        if pokemon_id != 0:
            for pokemon in self.pokemon:
                if pokemon["pokedexId"] == pokemon_id:
                    hits.append(pokemon)
        return hits

    def _get_by_name(self, pokemon_name):
        hits = []
        for pokemon in self.pokemon:
            if pokemon["name"] == pokemon_name:
                hits.append(pokemon)
        return hits

    def have(self, pokemon):
        if isinstance(pokemon, Pokemon):
            if pokemon.pokedex_id != 0:
                return self._have_by_id(pokemon.pokedex_id)
            return self._have_by_name(pokemon.name)
        return self._have_by_name(pokemon)

    def need(self, pokemon):
        return self.have(pokemon) is False

    def get_pokemon(self, pokemon):
        if isinstance(pokemon, Pokemon):
            if pokemon.pokedex_id != 0:
                return self._get_by_id(pokemon.pokedex_id)
            return self._get_by_name(pokemon.name)
        return self._get_by_name(pokemon)

    def get_pokemon_data(self, pokemon_id, default_value=None):
        return self.pokemon_data.get(str(pokemon_id), default_value)

    def set_pokemon_data(self, pokemon_id, pokemon_data):
        self.pokemon_data[str(pokemon_id)] = pokemon_data

    def update_pokemon_data(self, pokemon={}, pokemon_data={}):
        to_save = self.get_pokemon_data(pokemon["id"], default_value={})
        to_save.update({k: pokemon[k] for k in pokemon.keys() if k in [
            "lvl", "nickname", "locked", "pokedexId", "isShiny",
            "isBuddy", "avgIV", "sellPrice", "caughtAt"
        ]})
        to_save.update({k: pokemon_data[k] for k in pokemon_data.keys() if k in [
            "originalOwner", "originalChannel", "hpIv", "attackIv",
            "specialAttackIv", "defenseIv", "specialDefenseIv",
            "speedIv", "hpIvINT", "attackIvINT", "specialAttackIvINT",
            "defenseIvINT", "specialDefenseIvINT", "speedIvINT", "moves",
            "statUp", "statDown"
        ]})
        self.set_pokemon_data(pokemon["id"], to_save)
