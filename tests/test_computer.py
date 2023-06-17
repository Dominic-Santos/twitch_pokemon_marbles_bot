TEST_COMPUTER = [{
    "id": 16505571,
    "lvl": 14,
    "nickname": "Magikarp\u2640",
    "current_hp": 31,
    "max_hp": 31,
    "locked": False,
    "pokedexId": 10391,
    "order": 129,
    "baseStats": 200,
    "isShiny": False,
    "publicBattleBanned": False,
    "isBuddy": False,
    "avgIV": 16.833333333333332,
    "sellPrice": 103,
    "caughtAt": "2023-02-08T12:34:31.443Z",
    "hpPercent": 100.0,
    "specialVariant": 0,
    "name": "Magikarp"
}, {
    "id": 13409144,
    "lvl": 14,
    "nickname": None,
    "current_hp": 29,
    "max_hp": 29,
    "locked": False,
    "pokedexId": 129,
    "order": 129,
    "baseStats": 200,
    "isShiny": False,
    "publicBattleBanned": False,
    "isBuddy": False,
    "avgIV": 14.666666666666666,
    "sellPrice": 90,
    "caughtAt": "2022-11-27T12:01:03.698Z",
    "hpPercent": 100.0,
    "specialVariant": 0,
    "name": "Magikarp"
}, {
    "id": 15496549,
    "lvl": 14,
    "nickname": None,
    "current_hp": 34,
    "max_hp": 34,
    "locked": False,
    "pokedexId": 25,
    "order": 25,
    "baseStats": 320,
    "isShiny": False,
    "publicBattleBanned": False,
    "isBuddy": False,
    "avgIV": 13.166666666666666,
    "sellPrice": 185,
    "caughtAt": "2023-01-17T03:47:58.524Z",
    "hpPercent": 100.0,
    "specialVariant": 0,
    "name": "Pikachu"
}, {
    "id": 16896546,
    "lvl": 4,
    "nickname": "tradeB\u2640",
    "current_hp": 20,
    "max_hp": 20,
    "locked": False,
    "pokedexId": 10372,
    "order": 229,
    "baseStats": 500,
    "isShiny": False,
    "publicBattleBanned": False,
    "isBuddy": False,
    "avgIV": 12.833333333333334,
    "sellPrice": 151,
    "caughtAt": "2023-02-17T22:04:14.582Z",
    "hpPercent": 100.0,
    "specialVariant": 0,
    "name": "Houndoom"
}]

from . import Computer
from . import Pokemon

COMPUTER = Computer()


def test_have_by_name():
    test_cases = [
        ("Magikarp", True),
        ("Houndoom", True),
        ("Pikachu", True),
        ("Charmander", False),
        ("Dragonite", False),
    ]
    COMPUTER.set({"allPokemon": TEST_COMPUTER})

    for poke_name, expected in test_cases:
        assert COMPUTER.have(poke_name) == expected


def test_get_by_name():
    test_cases = [
        ("Magikarp", 2),
        ("Houndoom", 1),
        ("Pikachu", 1),
        ("Charmander", 0),
        ("Dragonite", 0),
    ]

    COMPUTER.set({"allPokemon": TEST_COMPUTER})

    for poke_name, expected in test_cases:
        assert len(COMPUTER.get_pokemon(poke_name)) == expected


def test_get_by_pokemon():
    test_cases = [
        ("Magikarp", 0, 2),
        ("Magikarp", 10391, 1),
        ("Houndoom", 10372, 1),
        ("Pikachu", 0, 1),
        ("Charmander", 0, 0),
        ("Dragonite", 0, 0),
        ("NA", 123123, 0),
    ]

    COMPUTER.set({"allPokemon": TEST_COMPUTER})

    for poke_name, poke_id, expected in test_cases:
        poke_obj = Pokemon()
        poke_obj.name = poke_name
        poke_obj.pokedex_id = poke_id
        assert len(COMPUTER.get_pokemon(poke_obj)) == expected


def test_have_by_pokemon():
    test_cases = [
        ("Magikarp", 0, True),
        ("Magikarp", 10391, True),
        ("Houndoom", 10372, True),
        ("Pikachu", 0, True),
        ("Charmander", 0, False),
        ("Dragonite", 0, False),
        ("NA", 123123, False),
    ]

    COMPUTER.set({"allPokemon": TEST_COMPUTER})

    for poke_name, poke_id, expected in test_cases:
        poke_obj = Pokemon()
        poke_obj.name = poke_name
        poke_obj.pokedex_id = poke_id
        assert COMPUTER.have(poke_obj) == expected


def test_need_by_pokemon():
    test_cases = [
        ("Magikarp", 0, False),
        ("Magikarp", 10391, False),
        ("Houndoom", 10372, False),
        ("Pikachu", 0, False),
        ("Charmander", 0, True),
        ("Dragonite", 0, True),
        ("NA", 123123, True),
    ]

    COMPUTER.set({"allPokemon": TEST_COMPUTER})

    for poke_name, poke_id, expected in test_cases:
        poke_obj = Pokemon()
        poke_obj.name = poke_name
        poke_obj.pokedex_id = poke_id
        assert COMPUTER.need(poke_obj) == expected
