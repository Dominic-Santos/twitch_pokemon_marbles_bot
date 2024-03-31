from datetime import datetime

from . import (
    Chat,
    load_inventory_data,
    load_mission_data,
    load_pokedex,
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


def test_check_got_dragon_egg(monkeypatch):
    missions = load_mission_data("14")
    inventory = load_inventory_data("01")
    pokedex = load_pokedex()
    computer = {
        "allPokemon": [
            {
                "id": 28031618,
                "lvl": 14,
                "nickname": "\u2b50Bulbasaur",
                "current_hp": 38,
                "max_hp": 38,
                "locked": False,
                "pokedexId": 1,
                "order": 1,
                "isShiny": False,
                "publicBattleBanned": False,
                "isBuddy": True,
                "avgIV": 20.333333333333332,
                "sellPrice": 627,
                "caughtAt": str(datetime.utcnow()),
                "hpPercent": 100,
                "specialVariant": 0,
                "baseStats": 318,
                "speed": 45,
                "special_defense": 65,
                "special_attack": 65,
                "defense": 49,
                "attack": 49,
                "hp": 45,
                "name": "Bulbasaur"
            }
        ]
    }

    PCG.missions.set(missions)
    PCG.inventory.set(inventory)
    PCG.pokedex.set(pokedex)
    PCG.computer.set(computer)

    # 'username', 'token', 'channel', 'get_pokemon_token', 'pcg'
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

    """
    to test:
    def check_egg_hatched(self, current_buddy):
    def check_pokebuddy(self, cached=False):
    def set_buddy(self, pokemon):
    def hatch_egg(self):
    """
