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

    # 'username', 'token', 'channel', 'get_pokemon_token', 'pcg', 'PCG'
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
    discord = create_mock_discord()

    # 'username', 'token', 'channel', 'get_pokemon_token', 'pcg', 'PCG'
    client = Chat.ClientIRCPokemon('username', 'token', 'channel', 'get_pokemon_token', True, PCG)
    client.log = logger.log
    client.pokemon.poke_buddy = egg.copy()
    client.pokemon.discord = discord

    PCG.settings["alert_egg_hatched"] = True
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


def test_set_buddy():
    logger = MockLogger()
    discord = create_mock_discord()
    api = MockApi()
    
    # 'username', 'token', 'channel', 'get_pokemon_token', 'pcg', 'PCG'
    client = Chat.ClientIRCPokemon('username', 'token', 'channel', 'get_pokemon_token', True, PCG)
    client.log = logger.log
    client.pokemon.discord = discord
    client.pokemon_api = api

    egg = {
        "id": 1,
        "pokedexId": 999000,
        "name": "Dragon Egg",
        "nickname": None
    }

    client.pokemon.settings["alert_buddy_changed"] = True

    client.set_buddy(egg)
    assert len(api.requests) == 1
    assert len(logger.calls) == 1
    assert len(discord.api.requests) == 1

    client.pokemon.settings["alert_buddy_changed"] = False

    client.set_buddy(egg)
    assert len(api.requests) == 2
    assert len(logger.calls) == 2
    assert len(discord.api.requests) == 1


def test_hatch_egg():
    pokedex = load_pokedex()
    egg = {
        "id": 1,
        "pokedexId": 999000,
        "name": "Dragon Egg",
        "nickname": None 
    }
    bulbasaur = {
        "id": 2,
        "pokedexId": 1,
        "name": "Bulbasaur",
        "nickname": None 
    }
    computer = {
        "allPokemon": [egg.copy(), bulbasaur.copy()]
    }

    logger = MockLogger()
    discord = create_mock_discord()
    api = MockApi()

    PCG.pokedex.set(pokedex)
    PCG.computer.set(computer)

    # 'username', 'token', 'channel', 'get_pokemon_token', 'pcg', 'PCG'
    client = Chat.ClientIRCPokemon('username', 'token', 'channel', 'get_pokemon_token', True, PCG)
    client.log = logger.log
    client.pokemon.discord = discord
    client.pokemon_api = api
    client.pokemon.poke_buddy = egg.copy()
    client.pokemon.settings["alert_buddy_changed"] = True

    client.hatch_egg()
    assert len(api.requests) == 0
    assert len(logger.calls) == 0
    assert len(discord.api.requests) == 0

    client.pokemon.poke_buddy = bulbasaur.copy()

    client.hatch_egg()
    assert len(api.requests) == 1
    assert len(logger.calls) == 1
    assert len(discord.api.requests) == 1

    client.pokemon.poke_buddy = None

    client.hatch_egg()
    assert len(api.requests) == 2
    assert len(logger.calls) == 2
    assert len(discord.api.requests) == 2


def test_check_pokebuddy():
    pokedex = load_pokedex()
    egg = {
        "id": 1,
        "pokedexId": 999000,
        "name": "Dragon Egg",
        "isBuddy": False,
        "nickname": None 
    }
    bulbasaur = {
        "id": 2,
        "pokedexId": 1,
        "name": "Bulbasaur",
        "isBuddy": True,
        "nickname": None
    }
    computer = {
        "allPokemon": [egg.copy(), bulbasaur.copy()]
    }

    logger = MockLogger()
    discord = create_mock_discord()
    api = MockApi()

    PCG.pokedex.set(pokedex)
    PCG.computer.set(computer)

    # 'username', 'token', 'channel', 'get_pokemon_token', 'pcg', 'PCG'
    client = Chat.ClientIRCPokemon('username', 'token', 'channel', 'get_pokemon_token', True, PCG)
    client.log = logger.log
    client.pokemon.discord = discord
    client.pokemon_api = api

    client.pokemon.settings["alert_buddy_changed"] = True
    client.pokemon.settings["alert_egg_hatched"] = True
    client.pokemon.settings["hatch_eggs"] = False

    assert client.pokemon.poke_buddy is None

    client.check_pokebuddy(cached=True)
    assert len(api.requests) == 0
    assert len(logger.calls) == 0
    assert len(discord.api.requests) == 0
    assert client.pokemon.poke_buddy is not None
    assert client.pokemon.poke_buddy["name"] == "Bulbasaur"

    client.check_pokebuddy(cached=True)
    assert len(api.requests) == 0
    assert len(logger.calls) == 0
    assert len(discord.api.requests) == 0
    assert client.pokemon.poke_buddy is not None
    assert client.pokemon.poke_buddy["name"] == "Bulbasaur"

    client.pokemon.settings["hatch_eggs"] = True
    client.check_pokebuddy(cached=True)
    assert len(api.requests) == 1
    assert len(logger.calls) == 1
    assert len(discord.api.requests) == 1
    assert client.pokemon.poke_buddy is not None
    assert client.pokemon.poke_buddy["name"] == "Bulbasaur"

    method, url, payload = api.requests[-1]
    assert method == "POST"
    assert url.endswith("pokemon-set-buddy/")
    assert payload == {"pokemon_id": egg["id"]}

    bulbasaur["isBuddy"] = False
    egg["isBuddy"] = True
    computer = {
        "allPokemon": [egg.copy(), bulbasaur.copy()]
    }
    PCG.computer.set(computer)

    client.check_pokebuddy(cached=True)
    assert len(api.requests) == 1
    assert len(logger.calls) == 1
    assert len(discord.api.requests) == 1
    assert client.pokemon.poke_buddy is not None
    assert client.pokemon.poke_buddy["name"] == "Dragon Egg"

    bulbasaur["isBuddy"] = True
    egg["isBuddy"] = False
    computer = {
        "allPokemon": [egg.copy(), bulbasaur.copy()]
    }
    PCG.computer.set(computer)

    # detected a hatch (1 log 1 discord call) then swap buddy to new egg (1 of each)
    client.check_pokebuddy(cached=True)
    assert len(api.requests) == 2
    assert len(logger.calls) == 3
    assert len(discord.api.requests) == 3
    assert client.pokemon.poke_buddy is not None
    assert client.pokemon.poke_buddy["name"] == "Bulbasaur"
