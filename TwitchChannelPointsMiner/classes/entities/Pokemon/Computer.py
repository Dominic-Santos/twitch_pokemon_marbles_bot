from .Pokemon import Pokemon


class Computer(object):
    def __init__(self):
        self.pokemon = []

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
            if pokemon.pokemon_id != 0:
                return self._have_by_id(pokemon.pokemon_id)
            return self._have_by_name(pokemon.name)
        return self._have_by_name(pokemon)

    def need(self, pokemon):
        return self.have(pokemon) is False

    def get_pokemon(self, pokemon):
        if isinstance(pokemon, Pokemon):
            if pokemon.pokemon_id != 0:
                return self._get_by_id(pokemon.pokemon_id)
            return self._get_by_name(pokemon.name)
        return self._get_by_name(pokemon)
