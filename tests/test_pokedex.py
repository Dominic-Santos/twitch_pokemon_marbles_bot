import json

from . import Pokedex

JSON_FILE = "tests/pokedex.json"

REGION_VARIANTS = ["Sin Gliscor", "His Braviary", "His Zoroark", "His Voltorb", "Hisuian Braviary", "Gal Rapidash", "Gal Darmanitan", "Gal Weezing", "Galarian Weezing"]
FISH_POKEMON = ["Magikarp", "Kyogre", "His Gyarados"]

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
        assert pokedex.fish(pokemon) == True
    assert pokedex.fish("Pidgey") == False


def test_have():
    for pokemon in dex_json["dex"]:
        assert pokedex.have(pokemon["name"]) == True


def test_have_extra():
    assert pokedex.have("Wormadam (Sandy)") == True
    pokedex.pokemon["Wormadam"] = False
    assert pokedex.have("Wormadam (Sandy)") == False
    assert pokedex.have("Aegislash (Blade)") == True
    assert pokedex.have("Aegislash (Shield)") == True
    pokedex.pokemon["Aegislash"] = False
    assert pokedex.have("Aegislash (Blade)") == False
    assert pokedex.have("Aegislash (Shield)") == False
    assert pokedex.have("Ho-Oh") == True
    assert pokedex.have("Indeedee") == True
    assert pokedex.have("garbage") == FAIL_TO_FIND
    assert pokedex.have("Mime Jr.") == True
