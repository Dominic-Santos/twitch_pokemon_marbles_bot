ALTER = {
    "content": "** ID: 10369 | <@&1068127190614552667> | Hippopotas-female **",
    "mention_roles": [
        "1068127190614552667"
    ],
    "timestamp": "2023-02-22T22:19:19.764000+00:00"
}

NORMAL = {
    "content": "Hippopotas - <@&935874437574688778> - <@&935906365434634320> 330 - 49.5 KG ! <@&936750563473891408> | <@&967919166667513877>",
    "mention_roles": [
        "935906365434634320",
        "935874437574688778",
        "936750563473891408",
        "967919166667513877"
    ],
    "timestamp": "2023-02-22T22:19:15.235000+00:00"
}

BST_ROLE = {
    "content": "Copperajah - <@&935874381316522014> - <@&935906659199500338> <@&960299429288620173> - 650.0 KG - Heavy Ball ! <@&937386694573977692> + <@&950160825115623464> ++ <@&995842704099508294>",
    "mention_roles": [
        "995842704099508294",
        "950160825115623464",
        "960299429288620173",
        "935906659199500338",
        "937386694573977692",
        "935874381316522014"
    ],
    "timestamp": "2023-02-23T06:19:16.192000+00:00"
}

MISSIGNO = {
    "content": "ID 10112: @MissingNo. delay: 7 seconds",
    "mention_roles": [],
    "timestamp": "2023-02-23T06:19:16.192000+00:00"
}

ALOMARO = {
    "content": "ID 10115: @Alolan Marowak - <@&935874381316522014> - <@&935906036550868993> <@&935906553289113730> 425 - 34.0 KG - Phantom Ball ! <@&937386564554727514> delay: 4 seconds",
    "mention_roles": [
        "935906036550868993",
        "935906553289113730",
        "937386564554727514",
        "935874381316522014"
    ],
    "timestamp": "2023-03-07T00:05:06.053000+00:00",
}

VIVILLON = [
    {
        "content": "@Vivillon - @Tier : B - @Bug @Flying 411 - 17.0 KG - Net Ball ! @Generation : 6",
        "mention_roles": [],
        "timestamp": "2023-03-07T00:05:06.053000+00:00",
    }, {
        "content": "ID: 10127 | Vivillon-modern",
        "mention_roles": [],
        "timestamp": "2023-03-07T00:05:06.053000+00:00",
    },
]

BASCULEGION = [
    {
        "content": "Basculegion - <@&935874381316522014> - <@&935906085276119040> <@&935906553289113730> 530 - 110.0 KG - Net & Phantom Ball :o <@&1082369332505481266> :fish: <@&1099744172287742122>",
        "mention_roles": ["935906085276119040", "935906553289113730", "1099744172287742122", "1082369332505481266", "935874381316522014"],
        "timestamp": "2023-04-24T09:23:18.326000+00:00"
    },
    {
        "content": "ID 86320: @MissingNo. <@&1082369284912722041>",
        "mention_roles": ["1082369284912722041"],
        "timestamp": "2023-04-24T09:23:22.330000+00:00",
    }
]

from . import Pokemon, PokemonCG

POKEMON = PokemonCG.PokemonComunityGame()
# PING = Pokeping()


def mock_data(to_return):
    def wrapped(limit=1):
        return to_return

    return wrapped


def set_mock_data(mock):
    POKEMON.pokeping.get_messages = mock_data(mock[::-1])


def test_normal():
    pokemon = POKEMON.pokeping.parse_pokemon(NORMAL)

    assert isinstance(pokemon, Pokemon)
    assert pokemon.name == "Hippopotas"
    assert pokemon.is_alternate is False
    assert pokemon.pokemon_id == 0
    assert pokemon.alt_name == "NA"
    assert pokemon.bst == 330
    assert pokemon.weight == 49.5


def test_alter_half():
    pokemon = POKEMON.pokeping.parse_pokemon(ALTER)

    assert isinstance(pokemon, Pokemon)
    assert pokemon.name == "NA"
    assert pokemon.is_alternate
    assert pokemon.pokemon_id == 10369
    assert pokemon.alt_name == "Hippopotas-female"
    assert pokemon.bst == -1
    assert pokemon.weight == -1


def test_bst_role():
    pokemon = POKEMON.pokeping.parse_pokemon(BST_ROLE)

    assert isinstance(pokemon, Pokemon)
    assert pokemon.name == "Copperajah"
    assert pokemon.is_alternate is False
    assert pokemon.pokemon_id == 0
    assert pokemon.alt_name == "NA"
    assert pokemon.bst == 500
    assert pokemon.weight == 650.0


def test_missingno():
    pokemon = POKEMON.pokeping.parse_pokemon(MISSIGNO)

    assert isinstance(pokemon, Pokemon)
    assert pokemon.name == "NA"
    assert pokemon.is_alternate is False
    assert pokemon.pokemon_id == 10112
    assert pokemon.alt_name == "NA"
    assert pokemon.bst == -1
    assert pokemon.weight == -1


def test_alomaro():
    pokemon = POKEMON.pokeping.parse_pokemon(ALOMARO)

    assert isinstance(pokemon, Pokemon)
    assert pokemon.name == "Alolan Marowak"
    assert pokemon.pokemon_id == 10115
    assert "Fire" in pokemon.types
    assert "Ghost" in pokemon.types
    assert pokemon.weight == 34.0
    assert pokemon.bst == 425


def test_vivillon():
    set_mock_data(VIVILLON)
    pokemon = POKEMON.pokeping.get_pokemon()
    assert pokemon.is_alternate
    assert pokemon.name == "Vivillon"
    assert "Bug" in pokemon.types
    assert "Flying" in pokemon.types
    assert pokemon.pokemon_id == 10127


def test_basculegion():
    set_mock_data(BASCULEGION)
    pokemon = POKEMON.pokeping.get_pokemon()
    assert pokemon.name == "Basculegion"
    assert "Water" in pokemon.types
    assert "Ghost" in pokemon.types
    assert pokemon.pokemon_id == 86320
