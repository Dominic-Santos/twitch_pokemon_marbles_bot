import json

from . import Pokedex, Pokemon

JSON_FILE = "tests/pokedex.json"

REGION_VARIANTS = ["Sin Gliscor", "His Braviary", "His Zoroark", "His Voltorb", "Hisuian Braviary", "Gal Rapidash", "Gal Darmanitan", "Gal Weezing", "Galarian Weezing"]
FISH_POKEMON = ["Magikarp", "Kyogre", "His Gyarados", "Gyarados"]

FAIL_TO_FIND = None
pokedex = Pokedex()


def load_pokedex():
    with open(JSON_FILE) as of:
        data = json.load(of)
    return data


dex_json = load_pokedex()
pokedex.set(dex_json)


def test_tiers():
    for i in range(1, pokedex.total + 1):
        pokemon = pokedex.stats(str(i))
        assert pokemon != FAIL_TO_FIND
        assert pokemon.tier != "NA"


def test_fish():
    for pokemon in FISH_POKEMON:
        assert pokedex.fish(pokemon)
    assert pokedex.fish("Pidgey") == False


def test_have():
    poke = Pokemon()
    for pokemon in dex_json["dex"]:
        poke.pokedex_id = pokemon["pokedexId"]
        assert pokedex.have(poke)


def test_baby():
    poke = Pokemon()
    poke.pokedex_id = 10  # Caterpie
    assert pokedex.baby(poke)
    poke.pokedex_id = 172  # Pichu
    assert pokedex.baby(poke)
    poke.pokedex_id = 249  # Lugia
    assert pokedex.baby(poke) == False


def test_clean_name():
    assert pokedex.clean_name("Gal Rapidash") == "Rapidash"
    poke = Pokemon()
    poke.name = "His Caterpie"
    assert pokedex.clean_name(poke) == "Caterpie"


def test_dogs():
    poke = Pokemon()
    poke.pokedex_id = 58  # Growlithe
    assert pokedex.dog(poke)
    poke.pokedex_id = 59  # Arcanine
    assert pokedex.dog(poke)
    poke.pokedex_id = 16  # Pidgey
    assert pokedex.dog(poke) == False


def test_cats():
    poke = Pokemon()
    poke.pokedex_id = 52  # Meowth
    assert pokedex.cat(poke)
    poke.pokedex_id = 53  # Persian
    assert pokedex.cat(poke)
    poke.pokedex_id = 16  # Pidgey
    assert pokedex.cat(poke) == False
