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
