from . import Pokedex, Pokemon, load_pokedex

FAIL_TO_FIND = None
pokedex = Pokedex()

dex_json = load_pokedex()
pokedex.set(dex_json)


def test_tiers():
    for i in range(1, pokedex.total + 1):
        pokemon = pokedex.stats(str(i))
        assert pokemon != FAIL_TO_FIND
        assert pokemon.tier != "NA"


def test_fish():
    poke = Pokemon()
    poke.pokedex_id = 129  # Magikarp
    assert pokedex.fish(poke)
    poke.pokedex_id = 883  # Arctovish
    assert pokedex.fish(poke)
    poke.pokedex_id = 16  # Pidgey
    assert pokedex.fish(poke) == False

    pokeobj = pokedex.stats(129)
    assert pokeobj.is_fish
    pokeobj = pokedex.stats(16)
    assert pokeobj.is_fish is False


def test_have():
    poke = Pokemon()
    for pokemon in dex_json["dex"]:
        poke = pokedex.stats(pokemon["pokedexId"])
        assert pokedex.have(poke)
        if pokemon["pokedexId"] > pokedex.total:
            assert pokedex.have_alt(poke) is False


def test_baby():
    poke = Pokemon()
    poke.pokedex_id = 10  # Caterpie
    assert pokedex.baby(poke)
    poke.pokedex_id = 172  # Pichu
    assert pokedex.baby(poke)
    poke.pokedex_id = 249  # Lugia
    assert pokedex.baby(poke) == False

    pokeobj = pokedex.stats(10)
    assert pokeobj.is_baby
    pokeobj = pokedex.stats(249)
    assert pokeobj.is_baby is False


def test_clean_name():
    assert pokedex.clean_name("Gal Rapidash") == "Rapidash"
    poke = Pokemon()
    poke.name = "His Caterpie"
    assert pokedex.clean_name(poke) == "Caterpie"
    poke.name = "His Arcanine"
    assert pokedex.clean_name(poke) == "Arcanine"


def test_dogs():
    poke = Pokemon()
    poke.pokedex_id = 58  # Growlithe
    assert pokedex.dog(poke)
    poke.pokedex_id = 59  # Arcanine
    assert pokedex.dog(poke)
    poke.pokedex_id = 16  # Pidgey
    assert pokedex.dog(poke) == False

    pokeobj = pokedex.stats(58)
    assert pokeobj.is_dog
    pokeobj = pokedex.stats(16)
    assert pokeobj.is_dog is False

    # alt dogs
    for poke_id in [10116, 10117, 10341, 10342, 10343, 10344, 10345, 10346, 10347, 10348, 10349, 10372, 10472, 10473, 10474, 10475, 10476, 10477, 10478, 10479, 10480, 10481, 10482, 10483, 10484, 10485, 10486, 10487, 10488, 86316, 86319, 86322, 86323, 100009]:
        pokeobj = pokedex.stats(poke_id)
        assert pokeobj.is_dog
        assert pokedex.dog(pokeobj)


def test_cats():
    poke = Pokemon()
    poke.pokedex_id = 52  # Meowth
    assert pokedex.cat(poke)
    poke.pokedex_id = 53  # Persian
    assert pokedex.cat(poke)
    poke.pokedex_id = 16  # Pidgey
    assert pokedex.cat(poke) == False

    pokeobj = pokedex.stats(52)
    assert pokeobj.is_cat
    pokeobj = pokedex.stats(16)
    assert pokeobj.is_cat is False

    # alt cats
    for poke_id in [10025, 10107, 10108, 10387, 10388, 10400, 10445, 86325]:
        pokeobj = pokedex.stats(poke_id)
        assert pokeobj.is_cat
        assert pokedex.cat(pokeobj)


def test_starter():
    poke = Pokemon()
    poke.pokedex_id = 1  # Bulabasaur
    assert pokedex.starter(poke)
    poke.pokedex_id = 906  # Sprigatito
    assert pokedex.starter(poke)
    poke.pokedex_id = 16  # Pidgey
    assert pokedex.starter(poke) == False

    pokeobj = pokedex.stats(1)
    assert pokeobj.is_starter
    pokeobj = pokedex.stats(16)
    assert pokeobj.is_starter is False


def test_legendary():
    poke = Pokemon()
    poke.pokedex_id = 151  # Mew
    assert pokedex.legendary(poke)
    poke.pokedex_id = 898  # Calyrex
    assert pokedex.legendary(poke)
    poke.pokedex_id = 16  # Pidgey
    assert pokedex.legendary(poke) == False

    pokeobj = pokedex.stats(151)
    assert pokeobj.is_legendary
    pokeobj = pokedex.stats(16)
    assert pokeobj.is_legendary is False
