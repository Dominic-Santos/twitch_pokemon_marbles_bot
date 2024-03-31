from datetime import datetime

from . import (
    Chat,
    load_inventory_data,
    load_mission_data,
    load_pokedex,
    Pokemon,
    PokemonComunityGame,
    MockLogger,
    MockDiscord,
)

PCG = PokemonComunityGame()


def test_egg_catch_reasons():
    inventory = load_inventory_data("01")
    PCG.inventory.set(inventory)

    poke = Pokemon()
    poke.pokedex_id = 25
    poke.name = "Pikachu"

    reason, ball = PCG.egg_catch_reasons(poke, None)
    assert reason is None
    assert ball is None

    buddy = Pokemon()
    buddy.name = "Egg"

    buddy.pokedex_id = 1
    reason, ball = PCG.egg_catch_reasons(poke, buddy)
    assert reason is None
    assert ball is None

    buddy.pokedex_id = 999000
    reason, ball = PCG.egg_catch_reasons(poke, buddy)
    assert reason == "catch"
    assert ball is None

    buddy.pokedex_id = 999001
    reason, ball = PCG.egg_catch_reasons(poke, buddy)
    assert reason == "ball"
    assert ball == "premier"

    buddy.pokedex_id = 999003
    reason, ball = PCG.egg_catch_reasons(poke, buddy)
    assert reason == "bst"
    assert ball is None

    poke.attack = 500
    reason, ball = PCG.egg_catch_reasons(poke, buddy)
    assert reason is None
    assert ball is None


def test_egg_trade_reasons():
    inventory = load_inventory_data("01")
    PCG.inventory.set(inventory)

    poke = Pokemon()
    poke.pokedex_id = 25
    poke.name = "Pikachu"
    poke.types = ["Electric"]

    reasons = PCG.egg_trade_reasons(poke, None)
    assert len(reasons) == 0

    buddy = Pokemon()
    buddy.name = "Egg"

    buddy.pokedex_id = 999001
    reasons = PCG.egg_trade_reasons(poke, buddy)
    assert len(reasons) == 0

    buddy.pokedex_id = 999004
    reasons = PCG.egg_trade_reasons(poke, buddy)
    assert len(reasons) == 0

    poke.types = ["Fire", "Grass", "Water"]
    buddy.pokedex_id = 999001
    reasons = PCG.egg_trade_reasons(poke, buddy)
    assert len(reasons) == 0

    buddy.pokedex_id = 999004
    reasons = PCG.egg_trade_reasons(poke, buddy)
    assert len(reasons) == 3


def test_check_got_dragon_egg():
    pokedex = load_pokedex()
    computer = {
        "allPokemon": [
            {
                "id": 1,
                "pokedexId": 1,
                "isBuddy": True,
                "caughtAt": str(datetime.utcnow()),
                "name": "Bulbasaur"
            }
        ]
    }

    PCG.pokedex.set(pokedex)
    PCG.computer.set(computer)

    # 'username', 'token', 'channel', 'get_pokemon_token', 'pcg', 'PCGd'
    client = Chat.ClientIRCPokemon('username', 'token', 'channel', 'get_pokemon_token', True, PCG)

    poke_obj, poke_bag = client.check_got_dragon_egg()
    assert poke_bag is None
    assert poke_obj is None

    # change bulbasaur to egg
    computer["allPokemon"][0].update({
        "pokedexId": 999000,
        "name": "Dragon Egg",
    })
    PCG.computer.set(computer)
    poke_obj, poke_bag = client.check_got_dragon_egg()
    assert poke_bag == computer["allPokemon"][0]
    assert isinstance(poke_obj, Pokemon)
    assert poke_obj.pokedex_id == 999000

    # change egg to old one
    computer["allPokemon"][0].update({
        "caughtAt": "2023-10-21T02:58:50.117Z",
    })
    poke_obj, poke_bag = client.check_got_dragon_egg()
    assert poke_bag is None
    assert poke_obj is None


def test_check_egg_hatched():
    pokedex = load_pokedex()
    egg = {
        "id": 1,
        "pokedexId": 999000,
        "isBuddy": True,
        "name": "Dragon Egg"
    }
    bulbasaur = {
        "id": 2,
        "pokedexId": 1,
        "isBuddy": True,
        "name": "Bulbasaur"
    }
    computer = {
        "allPokemon": [egg.copy()]
    }

    PCG.pokedex.set(pokedex)
    PCG.computer.set(computer)

    logger = MockLogger()
    discord = MockDiscord()
    auth_data = {
        "auth": "fakeuser",
        "user": "fakeuser"
    }
    discord.set(auth_data)
    discord.connect()

    # 'username', 'token', 'channel', 'get_pokemon_token', 'pcg', 'PCGd'
    client = Chat.ClientIRCPokemon('username', 'token', 'channel', 'get_pokemon_token', True, PCG)
    client.log = logger.log
    client.pokemon.poke_buddy = egg.copy()
    client.pokemon.discord = discord

    client.check_egg_hatched(egg)
    assert len(logger.calls) == 0
    assert len(discord.api.requests) == 0

    client.check_egg_hatched(bulbasaur)
    assert len(logger.calls) == 1
    assert len(discord.api.requests) == 1

    PCG.settings["alert_egg_hatched"] = False
    client.check_egg_hatched(bulbasaur)
    assert len(logger.calls) == 2
    assert len(discord.api.requests) == 1

    logger.reset()
    discord.api.reset()

    client.pokemon.poke_buddy = bulbasaur.copy()
    client.check_egg_hatched(bulbasaur)
    assert len(logger.calls) == 0
    assert len(discord.api.requests) == 0

    client.check_egg_hatched(egg)
    assert len(logger.calls) == 0
    assert len(discord.api.requests) == 0

"""
to test:
def check_pokebuddy(self, cached=False):
def set_buddy(self, pokemon):
def hatch_egg(self):
"""
