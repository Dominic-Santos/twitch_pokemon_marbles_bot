from . import PokemonComunityGame, load_inventory_data, load_pokedex, load_mission_data, Pokemon

PCG = PokemonComunityGame()


def test_catch_ball_mission():
    missions = load_mission_data("14")
    inventory = load_inventory_data("01")
    pokedex = load_pokedex()

    PCG.missions.set(missions)
    PCG.inventory.set(inventory)
    PCG.pokedex.set(pokedex)

    assert PCG.missions.have_mission("ball")
    assert PCG.missions.data["ball"] == ["great"]

    poke = Pokemon()
    poke.pokedex_id = 25
    poke.name = "Pikachu"

    catch_reasons = PCG.need_pokemon(poke)
    assert "ball" in catch_reasons


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
