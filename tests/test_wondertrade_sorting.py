from datetime import datetime

from . import (
    Chat,
    create_mock_discord,
    load_inventory_data,
    load_mission_data,
    load_pokedex,
    MockApi,
    MockLogger,
    Pokemon,
    PokemonComunityGame,
)

PCG = PokemonComunityGame()

def test_auto_renaming():
    pokedex = load_pokedex()
    computer = {
        "allPokemon": [
            {
                "id": 1,
                "pokedexId": 999000,
                "name": "Dragon Egg",
                "nickname": None ,
                "isShiny": False,
                "lvl": 36,
                "avgIV": 16.333333333333332,
                "sellPrice": 722,
            },
            {
                "id": 1,
                "pokedexId": 999000,
                "name": "Dragon Egg",
                "nickname": None ,
                "isShiny": False,
                "lvl": 36,
                "avgIV": 16.333333333333332,
                "sellPrice": 722,
            },
            {
                "id": 3,
                "pokedexId": 1,
                "name": "Bulbasaur",
                "nickname": "tradeB",
                "isShiny": False,
                "lvl": 36,
                "avgIV": 15,
                "sellPrice": 722,
            },
            {
                "id": 4,
                "pokedexId": 1,
                "name": "Bulbasaur",
                "nickname": None,
                "isShiny": True,
                "lvl": 36,
                "avgIV": 13,
                "sellPrice": 722,
            }
            ,
            {
                "id": 5,
                "pokedexId": 1,
                "name": "Bulbasaur",
                "nickname": None,
                "isShiny": False,
                "lvl": 36,
                "avgIV": 12,
                "sellPrice": 722,
            }
        ]
    }

    PCG.pokedex.set(pokedex)
    PCG.computer.set(computer)

    # 'username', 'token', 'channel', 'get_pokemon_token', 'pcg', 'PCG'
    client = Chat.ClientIRCPokemon('username', 'token', 'channel', 'get_pokemon_token', True, PCG)

    pokedict = client.sort_computer_by_pokedex_id([1, 2, 3])
    assert len(pokedict.keys()) == 1
    assert len(pokedict[1]) == 2

    pokedict = client.sort_computer_by_pokedex_id()
    assert len(pokedict.keys()) == 2
    assert len(pokedict[1]) == 2
    assert len(pokedict[999000]) == 2

    changes = client.get_rename_suggestion(pokedict)
    assert len(changes) == 2
    bulba_1, bulba_2 = changes
    poke, nick = bulba_1
    assert poke["id"] == 3
    assert nick[1:] == "Bulbasaur"
    poke, nick = bulba_2
    assert poke["id"] == 5
    assert nick[1:] == "tradeB"


    # def rename_computer(self, changes):
    #     for pokemon, new_name in changes:
    #         if new_name is not None and len(new_name) > 12:
    #             self.log_file("yellow", f"Wont rename {pokemon['name']} from {pokemon['nickname']} to {new_name}, name too long")
    #             continue
    #         self.pokemon_api.set_name(pokemon['id'], new_name)

    #         # update data cache
    #         pokemon_data = self.get_pokemon_data(pokemon)
    #         pokemon_data["nickname"] = new_name
    #         self.pokemon.computer.set_pokemon_data(pokemon["id"], pokemon_data)

    #         self.log_file("yellow", f"Renamed {pokemon['name']} from {pokemon['nickname']} to {new_name}")
    #         sleep(0.5)



    # def sort_computer(self, pokedex_ids=[]):
    #     '''Sort all/specific pokemon in computer and rename duplicates'''
    #     all_pokemon = self.pokemon_api.get_all_pokemon()
    #     self.pokemon.sync_computer(all_pokemon)

    #     pokedict = self.sort_computer_by_pokedex_id()
    #     changes = self.get_rename_suggestion(pokedict)

    #     self.rename_computer(changes)
    #     self.pokemon.computer.save_computer()