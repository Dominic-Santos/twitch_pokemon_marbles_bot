from . import Inventory, Pokemon

INVENTORY = Inventory()

INVENTORY_DATA = {
    "cash": 21569,
    "allItems": [
        {
            "id": 107,
            "name": "Magnet Ball",
            "sprite_name": "magnet_ball",
            "amount": 3,
            "price": None,
            "type": 2,
            "sell_price": 300,
            "catchRate": "70%",
            "description": "A somewhat different Pok\u00e9 Ball that is more effective when attempting to catch Steel- or Electric-type Pok\u00e9mon.",
            "category": "ball",
            "tmType": None,
            "usable": False
        },
        {
            "id": 53,
            "name": "Pokedaily Reset",
            "sprite_name": "pokedaily_reset",
            "amount": 2,
            "price": None,
            "type": 1,
            "sell_price": 100,
            "catchRate": None,
            "description": "This item will reset the cooldown of your pokedaily!",
            "category": "extra",
            "tmType": None,
            "usable": True
        }, {
            "id": 52,
            "name": "Shiny Charm",
            "sprite_name": "shiny_charm",
            "amount": 1,
            "price": None,
            "type": 1,
            "sell_price": None,
            "catchRate": None,
            "description": "Reward for finishing the spawnable pokedex.\r\nDoubles the shiny chance for all catches (exception: cherish balls)",
            "category": "collectable",
            "tmType": None,
            "usable": False
        }, {
            "id": 28,
            "name": "Buddy Ball",
            "sprite_name": "buddy_ball",
            "amount": 6,
            "price": None,
            "type": 2,
            "sell_price": 400,
            "catchRate": "70%",
            "description": "A weird looking ball which is more effective on Pok\u00e9mon that share a type with your Buddy-Pok\u00e9mon.",
            "category": "ball",
            "tmType": None,
            "usable": False
        }, {
            "id": 14,
            "name": "Cherish Ball",
            "sprite_name": "cherish_ball",
            "amount": 10,
            "price": None,
            "type": 2,
            "sell_price": 1000,
            "catchRate": "30%",
            "description": "A quite rare Pok\u00e9 Ball that has been crafted in order to commemorate a special occasion of some sort. Increased chance to obtain a shiny Pok\u00e9mon.",
            "category": "ball",
            "tmType": None,
            "usable": False
        }, {
            "id": 27,
            "name": "Cipher Ball",
            "sprite_name": "cipher_ball",
            "amount": 1,
            "price": None,
            "type": 2,
            "sell_price": 300,
            "catchRate": "70%",
            "description": "A somewhat different Pok\u00e9 Ball that is more effective when attempting to catch Poison- or Psychic-type Pok\u00e9mon.",
            "category": "ball",
            "tmType": None,
            "usable": False
        }, {
            "id": 29,
            "name": "Clone Ball",
            "sprite_name": "clone_ball",
            "amount": 14,
            "price": None,
            "type": 2,
            "sell_price": 500,
            "catchRate": "30%",
            "description": "An experimental Ball which generates a second Pokemon from the one you originally catch with this ball",
            "category": "ball",
            "tmType": None,
            "usable": False
        }, {
            "id": 101,
            "name": "Dive Ball",
            "sprite_name": "dive_ball",
            "amount": 30,
            "price": None,
            "type": 2,
            "sell_price": None,
            "catchRate": "55%",
            "description": "A Ball that is more effective when attempting to catch\ud83d\udc1f Fish \ud83d\udc1fPok\u00e9mon.",
            "category": "ball",
            "tmType": None,
            "usable": False
        }, {
            "id": 22,
            "name": "Feather Ball",
            "sprite_name": "feather_ball",
            "amount": 17,
            "price": None,
            "type": 2,
            "sell_price": 400,
            "catchRate": "Scaling with weight 20% to 80%",
            "description": "A Pok\u00e9 Ball that is better than usual at catching very light Pok\u00e9mon.",
            "category": "ball",
            "tmType": None,
            "usable": False
        }, {
            "id": 34,
            "name": "Frozen Ball",
            "sprite_name": "frozen_ball",
            "amount": 1,
            "price": None,
            "type": 2,
            "sell_price": 300,
            "catchRate": "80%",
            "description": "An icy Ball. Most effective if used on Ice-type Pok\u00e9mon.",
            "category": "ball",
            "tmType": None,
            "usable": False
        }, {
            "id": 33,
            "name": "Night Ball",
            "sprite_name": "night_ball",
            "amount": 7,
            "price": None,
            "type": 2,
            "sell_price": 300,
            "catchRate": "80%",
            "description": "A gloomy ball. Works better on Dark-type Pok\u00e9mon.",
            "category": "ball",
            "tmType": None,
            "usable": False
        }, {
            "id": 32,
            "name": "Phantom Ball",
            "sprite_name": "phantom_ball",
            "amount": 2,
            "price": None,
            "type": 2,
            "sell_price": 300,
            "catchRate": "80%",
            "description": "A creepy looking ball. Higher catch rate on Ghost type Pok\u00e9mon.",
            "category": "ball",
            "tmType": None,
            "usable": False
        }, {
            "id": 3,
            "name": "Great Ball",
            "sprite_name": "great_ball",
            "amount": 13,
            "price": 600,
            "type": 2,
            "sell_price": 300,
            "catchRate": "55%",
            "description": "A good, high-performance Pok\u00e9 Ball that provides a higher success rate for catching Pok\u00e9mon than a standard Pok\u00e9 Ball.",
            "category": "ball",
            "tmType": None,
            "usable": False
        }, {
            "id": 18,
            "name": "Great Cherish Ball",
            "sprite_name": "great_cherish_ball",
            "amount": 10,
            "price": None,
            "type": 2,
            "sell_price": 1500,
            "catchRate": "55%",
            "description": "A modified Cherish Ball with a better catch rate. Has a higher chance to catch a shiny Pokemon.",
            "category": "ball",
            "tmType": None,
            "usable": False
        }, {
            "id": 21,
            "name": "Heavy Ball",
            "sprite_name": "heavy_ball",
            "amount": 22,
            "price": None,
            "type": 2,
            "sell_price": 400,
            "catchRate": "Scaling with weight 20% to 80%",
            "description": "A Pok\u00e9 Ball that is better than usual at catching very heavy Pok\u00e9mon.",
            "category": "ball",
            "tmType": None,
            "usable": False
        }, {
            "id": 24,
            "name": "Net Ball",
            "sprite_name": "net_ball",
            "amount": 1,
            "price": None,
            "type": 2,
            "sell_price": 300,
            "catchRate": "70%",
            "description": "A somewhat different Pok\u00e9 Ball that is more effective when attempting to catch Water- or Bug-type Pok\u00e9mon.",
            "category": "ball",
            "tmType": None,
            "usable": False
        }, {
            "id": 2,
            "name": "Poke Ball",
            "sprite_name": "poke_ball",
            "amount": 127,
            "price": 300,
            "type": 2,
            "sell_price": 150,
            "catchRate": "30%",
            "description": "A device for catching wild Pok\u00e9mon. It's thrown like a ball at a Pok\u00e9mon, comfortably encapsulating its target.",
            "category": "ball",
            "tmType": None,
            "usable": False
        }, {
            "id": 20,
            "name": "Premier Ball",
            "sprite_name": "premier_ball",
            "amount": 36,
            "price": None,
            "type": 2,
            "sell_price": 100,
            "catchRate": "30%",
            "description": "A somewhat rare Pok\u00e9 Ball that was made as a commemorative item used to celebrate an event of some sort.",
            "category": "ball",
            "tmType": None,
            "usable": False
        }, {
            "id": 26,
            "name": "Quick Ball",
            "sprite_name": "quick_ball",
            "amount": 0,
            "price": None,
            "type": 2,
            "sell_price": 500,
            "catchRate": "Scaling with time 10% to 90%",
            "description": "A somewhat different Pok\u00e9 Ball that has a more successful catch rate if used at the start of a wild encounter.",
            "category": "ball",
            "tmType": None,
            "usable": False
        }, {
            "id": 97,
            "name": "Stone Ball",
            "sprite_name": "stone_ball",
            "amount": 7,
            "price": None,
            "type": 2,
            "sell_price": 500,
            "catchRate": "30%",
            "description": "A rare  ball with an increased chance to drop an evolution stone.",
            "category": "ball",
            "tmType": None,
            "usable": False
        }, {
            "id": 25,
            "name": "Timer Ball",
            "sprite_name": "timer_ball",
            "amount": 0,
            "price": None,
            "type": 2,
            "sell_price": 500,
            "catchRate": "Scaling with time 10% to 90%",
            "description": "A somewhat different Pok\u00e9 Ball that becomes progressively more effective at catching Pok\u00e9mon the closer the Pok\u00e9mon is to escaping.",
            "category": "ball",
            "tmType": None,
            "usable": False
        }, {
            "id": 4,
            "name": "Ultra Ball",
            "sprite_name": "ultra_ball",
            "amount": 14,
            "price": 1000,
            "type": 2,
            "sell_price": 500,
            "catchRate": "80%",
            "description": "An ultra-high-performance Pok\u00e9 Ball that provides a higher success rate for catching Pok\u00e9mon than a Great Ball.",
            "category": "ball",
            "tmType": None,
            "usable": False
        }, {
            "id": 19,
            "name": "Ultra Cherish Ball",
            "sprite_name": "ultra_cherish_ball",
            "amount": 12,
            "price": None,
            "type": 2,
            "sell_price": 2500,
            "catchRate": "80%",
            "description": "A modified Cherish Ball with a better catch rate. Has a higher chance to catch a shiny Pokemon.",
            "category": "ball",
            "tmType": None,
            "usable": False
        }, {
            "id": 40,
            "name": "Hyper Potion",
            "sprite_name": "hyper_potion",
            "amount": 8,
            "price": 400,
            "type": 3,
            "sell_price": 200,
            "catchRate": None,
            "description": "A spray-type medicine for treating wounds. It can be used to restore 120 HP to a single Pok\u00e9mon.",
            "category": "heal",
            "tmType": None,
            "usable": False
        }, {
            "id": 6,
            "name": "Max Potion",
            "sprite_name": "max_potion",
            "amount": 4,
            "price": 750,
            "type": 3,
            "sell_price": 300,
            "catchRate": None,
            "description": "A spray-type medicine for treating wounds. It can be used to completely restore the max HP of a single Pok\u00e9mon.",
            "category": "heal",
            "tmType": None,
            "usable": False
        }, {
            "id": 5,
            "name": "Potion",
            "sprite_name": "potion",
            "amount": 41,
            "price": 100,
            "type": 3,
            "sell_price": 50,
            "catchRate": None,
            "description": "A spray-type medicine for treating wounds. It can be used to restore 20 HP to a single Pok\u00e9mon.",
            "category": "heal",
            "tmType": None,
            "usable": False
        }, {
            "id": 36,
            "name": "Revive",
            "sprite_name": "revive",
            "amount": 8,
            "price": 150,
            "type": 3,
            "sell_price": 75,
            "catchRate": None,
            "description": "A medicine that can be used to revive a single Pok\u00e9mon that has fainted. It also restores half of the Pok\u00e9mon's max HP.",
            "category": "heal",
            "tmType": None,
            "usable": False
        }, {
            "id": 39,
            "name": "Super Potion",
            "sprite_name": "super_potion",
            "amount": 10,
            "price": 250,
            "type": 3,
            "sell_price": 125,
            "catchRate": None,
            "description": "A spray-type medicine for treating wounds. It can be used to restore 60 HP to a single Pok\u00e9mon.",
            "category": "heal",
            "tmType": None,
            "usable": False
        }, {
            "id": 46,
            "name": "Battle Coin",
            "sprite_name": "battle_coin",
            "amount": 6,
            "price": None,
            "type": 4,
            "sell_price": 1000,
            "catchRate": None,
            "description": "Reward for joining a PCG tournament. This token can be spend on various rare items and Pok\u00e9mon in the battle coin shop or kept as reminiscence.",
            "category": "collectable",
            "tmType": None,
            "usable": False
        }, {
            "id": 45,
            "name": "Mood Mint",
            "sprite_name": "mood_mint",
            "amount": 1,
            "price": 7500,
            "type": 4,
            "sell_price": 5000,
            "catchRate": None,
            "description": "Delicious mint, which completly changes the nature of your pokemon.",
            "category": "battle",
            "tmType": None,
            "usable": False
        }, {
            "id": 102,
            "name": "TM Bubble Beam",
            "sprite_name": "tm_bubble_beam",
            "amount": 1,
            "price": None,
            "type": 4,
            "sell_price": 1000,
            "catchRate": None,
            "description": "Teaches a water type Pok\u00e9mon the move Bubble Beam. Randomly replaces one of the pokemon's water moves.",
            "category": "tm",
            "tmType": "water",
            "usable": False
        }, {
            "id": 44,
            "name": "Wonder Pass",
            "sprite_name": "wonder_pass",
            "amount": 1,
            "price": 3000,
            "type": 4,
            "sell_price": 1500,
            "catchRate": None,
            "description": "A rare pass that permits you to wonder trade again instantly.",
            "category": "extra",
            "tmType": None,
            "usable": True
        }, {
            "id": 82,
            "name": "Bug Stone",
            "sprite_name": "bug_stone",
            "amount": 3,
            "price": None,
            "type": 5,
            "sell_price": 1000,
            "catchRate": None,
            "description": "A stone that makes certain species of Pok\u00e9mon evolve. It is said that the stone's color determines the Pok\u00e9mon that will evolve.",
            "category": "evolution",
            "tmType": None,
            "usable": False
        }, {
            "id": 92,
            "name": "Dark Stone",
            "sprite_name": "dark_stone",
            "amount": 5,
            "price": None,
            "type": 5,
            "sell_price": 1000,
            "catchRate": None,
            "description": "A stone that makes certain species of Pok\u00e9mon evolve. It is said that the stone's color determines the Pok\u00e9mon that will evolve.",
            "category": "evolution",
            "tmType": None,
            "usable": False
        }, {
            "id": 91,
            "name": "Dragon Stone",
            "sprite_name": "dragon_stone",
            "amount": 3,
            "price": None,
            "type": 5,
            "sell_price": 1000,
            "catchRate": None,
            "description": "A stone that makes certain species of Pok\u00e9mon evolve. It is said that the stone's color determines the Pok\u00e9mon that will evolve.",
            "category": "evolution",
            "tmType": None,
            "usable": False
        }, {
            "id": 93,
            "name": "Fairy Stone",
            "sprite_name": "fairy_stone",
            "amount": 1,
            "price": None,
            "type": 5,
            "sell_price": 1000,
            "catchRate": None,
            "description": "A stone that makes certain species of Pok\u00e9mon evolve. It is said that the stone's color determines the Pok\u00e9mon that will evolve.",
            "category": "evolution",
            "tmType": None,
            "usable": False
        }, {
            "id": 77,
            "name": "Fighting Stone",
            "sprite_name": "fighting_stone",
            "amount": 1,
            "price": None,
            "type": 5,
            "sell_price": 1000,
            "catchRate": None,
            "description": "A stone that makes certain species of Pok\u00e9mon evolve. It is said that the stone's color determines the Pok\u00e9mon that will evolve.",
            "category": "evolution",
            "tmType": None,
            "usable": False
        }, {
            "id": 85,
            "name": "Fire Stone",
            "sprite_name": "fire_stone",
            "amount": 1,
            "price": None,
            "type": 5,
            "sell_price": 1000,
            "catchRate": None,
            "description": "A stone that makes certain species of Pok\u00e9mon evolve. It is said that the stone's color determines the Pok\u00e9mon that will evolve.",
            "category": "evolution",
            "tmType": None,
            "usable": False
        }, {
            "id": 78,
            "name": "Flying Stone",
            "sprite_name": "flying_stone",
            "amount": 2,
            "price": None,
            "type": 5,
            "sell_price": 1000,
            "catchRate": None,
            "description": "A stone that makes certain species of Pok\u00e9mon evolve. It is said that the stone's color determines the Pok\u00e9mon that will evolve.",
            "category": "evolution",
            "tmType": None,
            "usable": False
        }, {
            "id": 83,
            "name": "Ghost Stone",
            "sprite_name": "ghost_stone",
            "amount": 1,
            "price": None,
            "type": 5,
            "sell_price": 1000,
            "catchRate": None,
            "description": "A stone that makes certain species of Pok\u00e9mon evolve. It is said that the stone's color determines the Pok\u00e9mon that will evolve.",
            "category": "evolution",
            "tmType": None,
            "usable": False
        }, {
            "id": 87,
            "name": "Grass Stone",
            "sprite_name": "grass_stone",
            "amount": 2,
            "price": None,
            "type": 5,
            "sell_price": 1000,
            "catchRate": None,
            "description": "A stone that makes certain species of Pok\u00e9mon evolve. It is said that the stone's color determines the Pok\u00e9mon that will evolve.",
            "category": "evolution",
            "tmType": None,
            "usable": False
        }, {
            "id": 80,
            "name": "Ground Stone",
            "sprite_name": "ground_stone",
            "amount": 4,
            "price": None,
            "type": 5,
            "sell_price": 1000,
            "catchRate": None,
            "description": "A stone that makes certain species of Pok\u00e9mon evolve. It is said that the stone's color determines the Pok\u00e9mon that will evolve.",
            "category": "evolution",
            "tmType": None,
            "usable": False
        }, {
            "id": 90,
            "name": "Ice Stone",
            "sprite_name": "ice_stone",
            "amount": 1,
            "price": None,
            "type": 5,
            "sell_price": 1000,
            "catchRate": None,
            "description": "A stone that makes certain species of Pok\u00e9mon evolve. It is said that the stone's color determines the Pok\u00e9mon that will evolve.",
            "category": "evolution",
            "tmType": None,
            "usable": False
        }, {
            "id": 76,
            "name": "Normal Stone",
            "sprite_name": "normal_stone",
            "amount": 3,
            "price": None,
            "type": 5,
            "sell_price": 1000,
            "catchRate": None,
            "description": "A stone that makes certain species of Pok\u00e9mon evolve. It is said that the stone's color determines the Pok\u00e9mon that will evolve.",
            "category": "evolution",
            "tmType": None,
            "usable": False
        }, {
            "id": 79,
            "name": "Poison Stone",
            "sprite_name": "poison_stone",
            "amount": 2,
            "price": None,
            "type": 5,
            "sell_price": 1000,
            "catchRate": None,
            "description": "A stone that makes certain species of Pok\u00e9mon evolve. It is said that the stone's color determines the Pok\u00e9mon that will evolve.",
            "category": "evolution",
            "tmType": None,
            "usable": False
        }, {
            "id": 89,
            "name": "Psychic Stone",
            "sprite_name": "psychic_stone",
            "amount": 3,
            "price": None,
            "type": 5,
            "sell_price": 1000,
            "catchRate": None,
            "description": "A stone that makes certain species of Pok\u00e9mon evolve. It is said that the stone's color determines the Pok\u00e9mon that will evolve.",
            "category": "evolution",
            "tmType": None,
            "usable": False
        }, {
            "id": 81,
            "name": "Rock Stone",
            "sprite_name": "rock_stone",
            "amount": 2,
            "price": None,
            "type": 5,
            "sell_price": 1000,
            "catchRate": None,
            "description": "A stone that makes certain species of Pok\u00e9mon evolve. It is said that the stone's color determines the Pok\u00e9mon that will evolve.",
            "category": "evolution",
            "tmType": None,
            "usable": False
        }, {
            "id": 94,
            "name": "Shimmering Stone",
            "sprite_name": "shimmering_stone",
            "amount": 3,
            "price": None,
            "type": 5,
            "sell_price": 2500,
            "catchRate": None,
            "description": "A stone that makes certain species of Pok\u00e9mon evolve.",
            "category": "evolution",
            "tmType": None,
            "usable": False
        }, {
            "id": 84,
            "name": "Steel Stone",
            "sprite_name": "steel_stone",
            "amount": 2,
            "price": None,
            "type": 5,
            "sell_price": 1000,
            "catchRate": None,
            "description": "A stone that makes certain species of Pok\u00e9mon evolve. It is said that the stone's color determines the Pok\u00e9mon that will evolve.",
            "category": "evolution",
            "tmType": None,
            "usable": False
        }, {
            "id": 86,
            "name": "Water Stone",
            "sprite_name": "water_stone",
            "amount": 3,
            "price": None,
            "type": 5,
            "sell_price": 1000,
            "catchRate": None,
            "description": "A stone that makes certain species of Pok\u00e9mon evolve. It is said that the stone's color determines the Pok\u00e9mon that will evolve.",
            "category": "evolution",
            "tmType": None,
            "usable": False
        }, {
            "id": 67,
            "name": "Team Ghost Badge",
            "sprite_name": "team_ghost_badge",
            "amount": 1,
            "price": None,
            "type": 6,
            "sell_price": 100,
            "catchRate": None,
            "description": "Membership token of Team Ghost during the Halloween Event 2022",
            "category": "collectable",
            "tmType": None,
            "usable": False
        }],
    "show_daily_reward_message": False
}


def test_inventory():
    INVENTORY.set(INVENTORY_DATA)
    assert INVENTORY.other_balls.get("Fish", ["unknown"])[0] == "diveball"
    assert INVENTORY.special_balls.get("Psychic", ["unknown"])[0] == "cipherball"
    assert INVENTORY.special_balls.get("Ice", ["unknown"])[0] == "frozenball"
    assert INVENTORY.special_balls.get("Water", ["unknown"])[0] == "netball"
    assert INVENTORY.special_balls.get("Bug", ["unknown"])[0] == "netball"
    assert INVENTORY.special_balls.get("Dark", ["unknown"])[0] == "nightball"
    assert INVENTORY.special_balls.get("Ghost", ["unknown"])[0] == "phantomball"
    assert INVENTORY.special_balls.get("Electric", ["unknown"])[0] == "magnetball"
    assert INVENTORY.special_balls.get("Steel", ["unknown"])[0] == "magnetball"


def test_best_ball():
    pokemon = Pokemon()
    pokemon.types = ["Dark"]
    INVENTORY.set(INVENTORY_DATA)
    reasons = ["pokedex"]

    assert INVENTORY.get_catch_ball(pokemon, reasons) == "nightball"
    pokemon.types = []
    assert INVENTORY.get_catch_ball(pokemon, reasons) == "ultraball"
    INVENTORY.balls["ultraball"] = 0
    assert INVENTORY.get_catch_ball(pokemon, reasons) == "greatball"
    INVENTORY.balls["greatball"] = 0
    assert INVENTORY.get_catch_ball(pokemon, reasons) == "pokeball"
    INVENTORY.balls["pokeball"] = 0
    assert INVENTORY.get_catch_ball(pokemon, reasons) == "premierball"


def test_worst_ball():
    pokemon = Pokemon()
    INVENTORY.set(INVENTORY_DATA)
    reasons = ["attempt"]

    assert INVENTORY.get_catch_ball(pokemon, reasons) == "premierball"
    INVENTORY.balls["premierball"] = 0
    assert INVENTORY.get_catch_ball(pokemon, reasons) == "pokeball"
    INVENTORY.balls["pokeball"] = 0
    assert INVENTORY.get_catch_ball(pokemon, reasons) == "greatball"
    INVENTORY.balls["greatball"] = 0
    assert INVENTORY.get_catch_ball(pokemon, reasons) == "ultraball"


def test_save_ball():
    pokemon = Pokemon()
    pokemon.types = ["Dark"]
    pokemon.tier = "S"
    INVENTORY.set(INVENTORY_DATA)
    INVENTORY.money_saving = 1000
    INVENTORY.cash = 0
    reasons = ["pokedex"]

    assert INVENTORY.get_catch_ball(pokemon, reasons) == "nightball"
    pokemon.types = []
    assert INVENTORY.get_catch_ball(pokemon, reasons) == "ultraball"
    INVENTORY.balls["ultraball"] = 0
    assert INVENTORY.get_catch_ball(pokemon, reasons) == "greatball"
    INVENTORY.balls["greatball"] = 0
    assert INVENTORY.get_catch_ball(pokemon, reasons) == "pokeball"
    INVENTORY.balls["pokeball"] = 0
    assert INVENTORY.get_catch_ball(pokemon, reasons) == "premierball"

    INVENTORY.set(INVENTORY_DATA)
    INVENTORY.cash = 0
    INVENTORY.money_saving = 1000
    pokemon.tier = "A"
    assert INVENTORY.get_catch_ball(pokemon, reasons) == "ultraball"
    pokemon.tier = "B"
    pokemon.types = ["Dark"]
    assert INVENTORY.get_catch_ball(pokemon, reasons) == "nightball"
    pokemon.types = []
    assert INVENTORY.get_catch_ball(pokemon, reasons) == "greatball"
    pokemon.tier = "C"
    assert INVENTORY.get_catch_ball(pokemon, reasons) == "pokeball"
    INVENTORY.balls["pokeball"] = 0
    assert INVENTORY.get_catch_ball(pokemon, reasons) == "premierball"


def test_have_ball():
    INVENTORY.set(INVENTORY_DATA)
    for ball in ("pokeball", "ultraball", "ultracherishball", "greatcherishball", "cherishball"):
        assert INVENTORY.have_ball(ball)
