from . import PokemonComunityGame, load_inventory_data, Pokemon

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
