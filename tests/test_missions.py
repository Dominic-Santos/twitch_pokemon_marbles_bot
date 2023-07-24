from . import Missions, Pokemon
import json

MISSIONS = Missions()

MISSIONS_STR = """{"missions": [{"name": "Wondertrade normal types", "goal": 6, "progress": 2, "rewardItem": {"id": 76, "name": "Normal Stone", "description": "A stone that makes certain species of Pok\u00e9mon evolve. It is said that the stone's color determines the Pok\u00e9mon that will evolve.", "sprite_name": "normal_stone", "category": "evolution", "tmType": null, "amount": 2}, "rewardPokemon": null, "endDate": "9 minutes"}, {"name": "Participate in public battles using a grass type", "goal": 10, "progress": 12, "rewardItem": null, "rewardPokemon": {"id": 86321, "name": "His Voltorb", "description": "An enigmatic Pok\u00e9mon that happens to bear a resemblance to a Pok\u00e9 Ball. When excited, it discharges the electric current it has stored in its belly, then lets out a great, uproarious laugh.", "sprite_name": "hisuian-voltorb"}, "endDate": "9 minutes"}, {"name": "Win easy stadium battles", "goal": 5, "progress": 1, "rewardItem": {"id": 40, "name": "Hyper Potion", "description": "A spray-type medicine for treating wounds. It can be used to restore 120 HP to a single Pok\u00e9mon.", "sprite_name": "hyper_potion", "category": "heal", "tmType": null, "amount": 10}, "rewardPokemon": null, "endDate": "9 minutes"}, {"name": "Miss catches", "goal": 12, "progress": 5, "rewardItem": {"id": 97, "name": "Stone Ball", "description": "A rare  ball with an increased chance to drop an evolution stone.", "sprite_name": "stone_ball", "category": "ball", "tmType": null, "amount": 3}, "rewardPokemon": null, "endDate": "9 minutes"}, {"name": "???", "goal": 3, "progress": 6, "rewardItem": {"id": 79, "name": "Poison Stone", "description": "A stone that makes certain species of Pok\u00e9mon evolve. It is said that the stone's color determines the Pok\u00e9mon that will evolve.", "sprite_name": "poison_stone", "category": "evolution", "tmType": null, "amount": 1}, "rewardPokemon": null, "endDate": "9 minutes"}], "endDate": "9 minutes"}"""
MISSIONS_STR_2 = """{"missions": [{"name": "Catch fire type pokemon", "goal": 5, "progress": 0, "rewardItem": null, "rewardPokemon": {"id": 4, "name": "Charmander", "description": "From the time it is born, a flame burns at the tip of its tail. Its life would end if the flame were to go out.", "sprite_name": "charmander"}, "endDate": "6 days, 23 hours and 59 minutes"}, {"name": "???", "goal": 2, "progress": 0, "rewardItem": {"id": 25, "name": "Timer Ball", "description": "A somewhat different Pok\u00e9 Ball that becomes progressively more effective at catching Pok\u00e9mon the closer the Pok\u00e9mon is to escaping.", "sprite_name": "timer_ball", "category": "ball", "tmType": null, "amount": 7}, "rewardPokemon": null, "endDate": "6 days, 23 hours and 59 minutes"}, {"name": "Wondertrade Pok\u00e9mon with less than 383 BST", "goal": 10, "progress": 0, "rewardItem": {"id": 88, "name": "Electric Stone", "description": "A stone that makes certain species of Pok\u00e9mon evolve. It is said that the stone's color determines the Pok\u00e9mon that will evolve.", "sprite_name": "electric_stone", "category": "evolution", "tmType": null, "amount": 1}, "rewardPokemon": null, "endDate": "6 days, 23 hours and 59 minutes"}, {"name": "Use field effects in a battle", "goal": 2, "progress": 0, "rewardItem": {"id": 42, "name": "Empty Disc", "description": "An empty disc used to teach your Pok\u00e9mon a full new move set. Use it with caution.", "sprite_name": "empty_disc", "category": "battle", "tmType": null, "amount": 1}, "rewardPokemon": null, "endDate": "6 days, 23 hours and 59 minutes"}, {"name": "Miss catches", "goal": 25, "progress": 26, "rewardItem": {"id": 94, "name": "Shimmering Stone", "description": "A stone that makes certain species of Pok\u00e9mon evolve.", "sprite_name": "shimmering_stone", "category": "evolution", "tmType": null, "amount": 1}, "rewardPokemon": null, "endDate": "6 days, 23 hours and 59 minutes"}], "endDate": "6 days, 23 hours and 59 minutes"}"""
MISSIONS_STR_3 = """{"missions": [{"name": "Catch Pokemon heavier than 250kg / 551 lbs", "goal": 3, "progress": 0, "rewardItem": {"id": 4, "name": "Ultra Ball", "description": "An ultra-high-performance Pok\u00e9 Ball that provides a higher success rate for catching Pok\u00e9mon than a Great Ball.", "sprite_name": "ultra_ball", "category": "ball", "tmType": null, "amount": 5}, "rewardPokemon": null, "endDate": "6 days, 15 hours and 31 minutes"}, {"name": "Participate in public battles using a dark type", "goal": 10, "progress": 0, "rewardItem": null, "rewardPokemon": {"id": 258, "name": "Mudkip", "description": "In water, Mudkip breathes using the gills on its cheeks. If it is faced with a tight situation in battle, this Pok\u00e9mon will unleash its amazing power\u2014it can crush rocks bigger than itself.", "sprite_name": "mudkip"}, "endDate": "6 days, 15 hours and 31 minutes"}, {"name": "Use super effective moves", "goal": 50, "progress": 0, "rewardItem": {"id": 51, "name": "Team enhancer", "description": "Use this item to increase the amount of teams by 1! You can have up to 20 teams.", "sprite_name": "team_enhancer", "category": "extra", "tmType": null, "amount": 2}, "rewardPokemon": null, "endDate": "6 days, 15 hours and 31 minutes"}, {"name": "Wonder trade ground type Pok\u00e9mon", "goal": 7, "progress": 1, "rewardItem": {"id": 80, "name": "Ground Stone", "description": "A stone that makes certain species of Pok\u00e9mon evolve. It is said that the stone's color determines the Pok\u00e9mon that will evolve.", "sprite_name": "ground_stone", "category": "evolution", "tmType": null, "amount": 1}, "rewardPokemon": null, "endDate": "6 days, 15 hours and 31 minutes"}, {"name": "Catch ghost type Pok\u00e9mon", "goal": 5, "progress": 0, "rewardItem": {"id": 83, "name": "Ghost Stone", "description": "A stone that makes certain species of Pok\u00e9mon evolve. It is said that the stone's color determines the Pok\u00e9mon that will evolve.", "sprite_name": "ghost_stone", "category": "evolution", "tmType": null, "amount": 1}, "rewardPokemon": null, "endDate": "6 days, 15 hours and 31 minutes"}], "endDate": "6 days, 15 hours and 31 minutes"}"""
MISSIONS_STR_4 = """{"missions": [{"name": "Catch psychic type Pok\u00e9mon", "goal": 7, "progress": 0, "rewardItem": {"id": 29, "name": "Clone Ball", "description": "An experimental Ball which generates a second Pokemon from the one you originally catch with this ball", "sprite_name": "clone_ball", "category": "ball", "tmType": null, "amount": 3}, "rewardPokemon": null, "endDate": "6 days, 14 hours and 9 minutes"}, {"name": "Miss a catch", "goal": 15, "progress": 11, "rewardItem": {"id": 25, "name": "Timer Ball", "description": "A somewhat different Pok\u00e9 Ball that becomes progressively more effective at catching Pok\u00e9mon the closer the Pok\u00e9mon is to escaping.", "sprite_name": "timer_ball", "category": "ball", "tmType": null, "amount": 3}, "rewardPokemon": null, "endDate": "6 days, 14 hours and 9 minutes"}, {"name": "Wondertrade", "goal": 20, "progress": 3, "rewardItem": {"id": 42, "name": "Empty Disc", "description": "An empty disc used to teach your Pok\u00e9mon a full new move set. Use it with caution.", "sprite_name": "empty_disc", "category": "battle", "tmType": null, "amount": 2}, "rewardPokemon": null, "endDate": "6 days, 14 hours and 9 minutes"}, {"name": "Attempt catches", "goal": 50, "progress": 38, "rewardItem": {"id": 86, "name": "Water Stone", "description": "A stone that makes certain species of Pok\u00e9mon evolve. It is said that the stone's color determines the Pok\u00e9mon that will evolve.", "sprite_name": "water_stone", "category": "evolution", "tmType": null, "amount": 1}, "rewardPokemon": null, "endDate": "6 days, 14 hours and 9 minutes"}, {"name": "Catch Pok\u00e9mon with less than 333 BST", "goal": 10, "progress": 7, "rewardItem": {"id": 54, "name": "Total Reset", "description": "Total Reset used to teach your Pok\u00e9mon a full new move set, completely changes the nature of your pokemon and changes the individual values of a Pok\u00e9mon. Use it with caution.", "sprite_name": "total_reset", "category": "battle", "tmType": null, "amount": 1}, "rewardPokemon": null, "endDate": "6 days, 14 hours and 9 minutes"}, {"name": "Participate in public battles using a dragon type", "goal": 15, "progress": 0, "rewardItem": {"id": 2, "name": "Poke Ball", "description": "A device for catching wild Pok\u00e9mon. It's thrown like a ball at a Pok\u00e9mon, comfortably encapsulating its target.", "sprite_name": "poke_ball", "category": "ball", "tmType": null, "amount": 10}, "rewardPokemon": null, "endDate": "6 days, 14 hours and 9 minutes"}], "endDate": "6 days, 14 hours and 9 minutes"}"""
MISSIONS_STR_5 = """{"missions": [{"name": "Use super effective moves", "goal": 75, "progress": 0, "rewardItem": {"id": 42, "name": "Empty Disc", "description": "An empty disc used to teach your Pok\u00e9mon a full new move set. Use it with caution.", "sprite_name": "empty_disc", "category": "battle", "tmType": null, "amount": 2}, "rewardPokemon": null, "endDate": "6 days, 8 hours and 49 minutes"}, {"name": "Participate in public battles using a water type", "goal": 10, "progress": 0, "rewardItem": {"id": 24, "name": "Net Ball", "description": "A somewhat different Pok\u00e9 Ball that is more effective when attempting to catch Water- or Bug-type Pok\u00e9mon.", "sprite_name": "net_ball", "category": "ball", "tmType": null, "amount": 3}, "rewardPokemon": null, "endDate": "6 days, 8 hours and 49 minutes"}, {"name": "Catch Pokemon heavier than 250kg / 551 lbs", "goal": 2, "progress": 0, "rewardItem": {"id": 49, "name": "Present", "description": "Enter a chat and type !pokegift to make other players happy! \ud83c\udf85", "sprite_name": "present", "category": "event", "tmType": null, "amount": 3}, "rewardPokemon": null, "endDate": "6 days, 8 hours and 49 minutes"}, {"name": "Attempt catches", "goal": 35, "progress": 43, "rewardItem": null, "rewardPokemon": {"id": 816, "name": "Sobble", "description": "When it gets wet, its skin changes color, and this Pok\u00e9mon becomes invisible as if it were camouflaged.", "sprite_name": "sobble"}, "endDate": "6 days, 8 hours and 49 minutes"}, {"name": "Wondertrade steel types", "goal": 8, "progress": 5, "rewardItem": {"id": 84, "name": "Steel Stone", "description": "A stone that makes certain species of Pok\u00e9mon evolve. It is said that the stone's color determines the Pok\u00e9mon that will evolve.", "sprite_name": "steel_stone", "category": "evolution", "tmType": null, "amount": 1}, "rewardPokemon": null, "endDate": "6 days, 8 hours and 49 minutes"}, {"name": "Catch fish Pokemon!", "goal": 25, "progress": 24, "rewardItem": null, "rewardPokemon": {"id": 382, "name": "Kyogre", "description": "Kyogre is said to be the personification of the sea itself. Legends tell of its many clashes against Groudon, as each sought to gain the power of nature.", "sprite_name": "kyogre"}, "endDate": "13 days, 5 hours and 49 minutes"}, {"name": "Catch fish Pokemon!", "goal": 15, "progress": 24, "rewardItem": null, "rewardPokemon": {"id": 8, "name": "Wartortle", "description": "It cleverly controls its furry ears and tail to maintain its balance while swimming.", "sprite_name": "wartortle"}, "endDate": "13 days, 5 hours and 49 minutes"}, {"name": "Catch a fish 100% bigger than average!", "goal": 1, "progress": 0, "rewardItem": {"id": "hidden_item", "name": "???", "description": "???", "sprite_name": "hidden_item", "category": "extra", "tmType": null, "amount": 0}, "rewardPokemon": null, "endDate": "13 days, 5 hours and 49 minutes"}, {"name": "Catch a fish 25% smaller and 25% lighter!", "goal": 1, "progress": 3, "rewardItem": {"id": 94, "name": "Shimmering Stone", "description": "A stone that makes certain species of Pok\u00e9mon evolve.", "sprite_name": "shimmering_stone", "category": "evolution", "tmType": null, "amount": 1}, "rewardPokemon": null, "endDate": "13 days, 5 hours and 49 minutes"}, {"name": "Catch fish Pokemon!", "goal": 10, "progress": 24, "rewardItem": {"id": 102, "name": "TM Bubble Beam", "description": "Teaches a water type Pok\u00e9mon the move Bubble Beam. Randomly replaces one of the pokemon's water moves.", "sprite_name": "tm_bubble_beam", "category": "tm", "tmType": "water", "amount": 1}, "rewardPokemon": null, "endDate": "13 days, 5 hours and 49 minutes"}, {"name": "Catch a fish 75% smaller than average!", "goal": 1, "progress": 1, "rewardItem": null, "rewardPokemon": {"id": 657, "name": "Frogadier", "description": "Its swiftness is unparalleled. It can scale a tower of more than 2,000 feet in a minute\u2019s time.", "sprite_name": "frogadier"}, "endDate": "13 days, 5 hours and 49 minutes"}, {"name": "Catch fish Pokemon!", "goal": 1, "progress": 24, "rewardItem": {"id": 101, "name": "Dive Ball", "description": "A Ball that is more effective when attempting to catch\ud83d\udc1f Fish \ud83d\udc1fPok\u00e9mon.", "sprite_name": "dive_ball", "category": "ball", "tmType": null, "amount": 15}, "rewardPokemon": null, "endDate": "13 days, 5 hours and 49 minutes"}, {"name": "Catch fish Pokemon!", "goal": 5, "progress": 24, "rewardItem": {"id": 18, "name": "Great Cherish Ball", "description": "A modified Cherish Ball with a better catch rate. Has a higher chance to catch a shiny Pokemon.", "sprite_name": "great_cherish_ball", "category": "ball", "tmType": null, "amount": 3}, "rewardPokemon": null, "endDate": "13 days, 5 hours and 49 minutes"}, {"name": "Catch a fish 50% bigger than average!", "goal": 1, "progress": 2, "rewardItem": null, "rewardPokemon": {"id": 158, "name": "Totodile", "description": "Despite the smallness of its body, Totodile\u2019s jaws are very powerful. While the Pok\u00e9mon may think it is just playfully nipping, its bite has enough power to cause serious injury.", "sprite_name": "totodile"}, "endDate": "13 days, 5 hours and 49 minutes"}, {"name": "Catch a fish 100% heavier than average!", "goal": 1, "progress": 0, "rewardItem": {"id": "hidden_item", "name": "???", "description": "???", "sprite_name": "hidden_item", "category": "extra", "tmType": null, "amount": 0}, "rewardPokemon": null, "endDate": "13 days, 5 hours and 49 minutes"}, {"name": "Catch a fish 75% lighter than average!", "goal": 1, "progress": 3, "rewardItem": null, "rewardPokemon": {"id": 490, "name": "Manaphy", "description": "It starts its life with a wondrous power that permits it to bond with any kind of Pok\u00e9mon.", "sprite_name": "manaphy"}, "endDate": "13 days, 5 hours and 49 minutes"}, {"name": "Catch a fish 50% heavier than average!", "goal": 1, "progress": 4, "rewardItem": null, "rewardPokemon": {"id": 80, "name": "Slowbro", "description": "If this Pok\u00e9mon squeezes the tongue of the Shellder biting it, the Shellder will launch a toxic liquid from the tip of its shell.", "sprite_name": "slowbro"}, "endDate": "13 days, 5 hours and 49 minutes"}, {"name": "Catch fish Pokemon!", "goal": 20, "progress": 24, "rewardItem": {"id": 101, "name": "Dive Ball", "description": "A Ball that is more effective when attempting to catch\ud83d\udc1f Fish \ud83d\udc1fPok\u00e9mon.", "sprite_name": "dive_ball", "category": "ball", "tmType": null, "amount": 15}, "rewardPokemon": null, "endDate": "13 days, 5 hours and 49 minutes"}], "endDate": "6 days, 8 hours and 49 minutes"}"""
MISSIONS_STR_7 = """{"missions":[{"name":"Wonder trade Pokemon over 500 BST","goal":7,"progress":0,"rewardItem":{"id":44,"name":"Wonder Pass","description":"A rare pass that permits you to wonder trade again instantly.","sprite_name":"wonder_pass","category":"extra","tmType":null,"amount":3},"rewardPokemon":null,"endDate":"4 hours and 8 minutes"},{"name":"Catch fire type pokemon","goal":5,"progress":0,"rewardItem":null,"rewardPokemon":{"id":100007,"name":"Sin Ninetales","description":"While it will guide travelers who get lost on a snowy mountain down to the mountain’s base, it won’t forgive anyone who harms nature.","sprite_name":"sinister-ninetales"},"endDate":"4 hours and 8 minutes"},{"name":"Attempt catches","goal":30,"progress":0,"rewardItem":{"id":97,"name":"Stone Ball","description":"A rare  ball with an increased chance to drop an evolution stone.","sprite_name":"stone_ball","category":"ball","tmType":null,"amount":4},"rewardPokemon":null,"endDate":"4 hours and 8 minutes"},{"name":"Use super effective moves","goal":75,"progress":0,"rewardItem":{"id":42,"name":"Empty Disc","description":"An empty disc used to teach your Pokémon a full new move set. Use it with caution.","sprite_name":"empty_disc","category":"battle","tmType":null,"amount":6},"rewardPokemon":null,"endDate":"4 hours and 8 minutes"},{"name":"Participate in ranked battles","goal":5,"progress":0,"rewardItem":{"id":46,"name":"Battle Coin","description":"Reward for joining a PCG tournament. This token can be spend on various rare items and Pokémon in the battle coin shop or kept as reminiscence.","sprite_name":"battle_coin","category":"collectable","tmType":null,"amount":1},"rewardPokemon":null,"endDate":"4 hours and 8 minutes"},{"name":"Play stadium battles","goal":10,"progress":0,"rewardItem":{"id":43,"name":"IV Reset","description":"Completely changes the individual values of a Pokémon.","sprite_name":"iv_reset","category":"battle","tmType":null,"amount":4},"rewardPokemon":null,"endDate":"4 hours and 8 minutes"},{"name":"Use field effects in battles","goal":5,"progress":0,"rewardItem":{"id":45,"name":"Mood Mint","description":"Delicious mint, which completly changes the nature of your pokemon.","sprite_name":"mood_mint","category":"battle","tmType":null,"amount":4},"rewardPokemon":null,"endDate":"4 hours and 8 minutes"},{"name":"Miss fighting catches","goal":7,"progress":0,"rewardItem":{"id":77,"name":"Fighting Stone","description":"A stone that makes certain species of Pokémon evolve. It is said that the stone's color determines the Pokémon that will evolve.","sprite_name":"fighting_stone","category":"evolution","tmType":null,"amount":1},"rewardPokemon":null,"endDate":"4 hours and 8 minutes"},{"name":"???","goal":1,"progress":0,"rewardItem":{"id":"hidden_item","name":"???","description":"???","sprite_name":"hidden_item","category":"extra","tmType":null,"amount":5},"rewardPokemon":null,"endDate":"3 days, 1 hour and 8 minutes"},{"name":"???","goal":1,"progress":0,"rewardItem":{"id":108,"name":"Nest Ball","description":"A somewhat different Poké Ball that is more effective when used on a Pokémon that can evolve twice.","sprite_name":"nest_ball","category":"ball","tmType":null,"amount":5},"rewardPokemon":null,"endDate":"3 days, 1 hour and 8 minutes"},{"name":"[EVENT] Catch dragon type Pokemon!","goal":10,"progress":0,"rewardItem":null,"rewardPokemon":{"id":612,"name":"Haxorus","description":"While usually kindhearted, it can be terrifying if angered. Tusks that can slice through steel beams are how Haxorus deals with its adversaries.","sprite_name":"haxorus"},"endDate":"14 days, 1 hour and 8 minutes"},{"name":"[EVENT] Catch normal type Pokemon!","goal":40,"progress":0,"rewardItem":null,"rewardPokemon":{"id":773,"name":"Silvally","description":"The final factor needed to release this Pokémon’s true power was a strong bond with a Trainer it trusts.","sprite_name":"silvally"},"endDate":"14 days, 1 hour and 8 minutes"},{"name":"[EVENT] Catch dragon type Pokemon!","goal":20,"progress":0,"rewardItem":null,"rewardPokemon":{"id":86318,"name":"His Goodra","description":"Able to freely control the hardness of its metallic shell. It loathes solitude and is extremely clingy—it will fume and run riot if those dearest to it ever leave its side.","sprite_name":"hisuian-goodra"},"endDate":"14 days, 1 hour and 8 minutes"},{"name":"[EVENT] Catch dragon type Pokemon!","goal":40,"progress":0,"rewardItem":null,"rewardPokemon":{"id":10474,"name":"Silvally","description":"The final factor needed to release this Pokémon’s true power was a strong bond with a Trainer it trusts.","sprite_name":"silvally-dragon"},"endDate":"14 days, 1 hour and 8 minutes"},{"name":"[EVENT] Catch dragon or normal type Pokemon!","goal":50,"progress":0,"rewardItem":null,"rewardPokemon":{"id":483,"name":"Dialga","description":"It has the power to control time. It appears in Sinnoh-region myths as an ancient deity.","sprite_name":"dialga"},"endDate":"14 days, 1 hour and 8 minutes"},{"name":"[EVENT] Catch normal type Pokemon!","goal":20,"progress":0,"rewardItem":null,"rewardPokemon":{"id":10465,"name":"Sawsbuck","description":"They migrate according to the seasons, so some people call Sawsbuck the harbingers of spring.","sprite_name":"sawsbuck-summer"},"endDate":"14 days, 1 hour and 8 minutes"},{"name":"Win Challenge","goal":13,"progress":0,"rewardItem":null,"rewardPokemon":{"id":486,"name":"Regigigas","description":"There is an enduring legend that states this Pokémon towed continents with ropes.","sprite_name":"regigigas"},"endDate":"14 days, 1 hour and 8 minutes"},{"name":"[EVENT] Catch normal type Pokemon!","goal":10,"progress":0,"rewardItem":null,"rewardPokemon":{"id":143,"name":"Snorlax","description":"This Pokémon’s stomach is so strong, even eating moldy or rotten food will not affect it.","sprite_name":"snorlax"},"endDate":"14 days, 1 hour and 8 minutes"}],"endDate":"4 hours and 8 minutes"}"""
MISSIONS_STR_8 = """{"missions":[{"name":"???","goal":1,"progress":3,"rewardItem":{"id":19,"name":"Ultra Cherish Ball","description":"A modified Cherish Ball with a better catch rate. Has a higher chance to catch a shiny Pokemon.","sprite_name":"ultra_cherish_ball","category":"ball","tmType":null,"amount":2},"rewardPokemon":null,"endDate":"13 hours and 34 minutes"},{"name":"???","goal":1,"progress":2,"rewardItem":{"id":19,"name":"Ultra Cherish Ball","description":"A modified Cherish Ball with a better catch rate. Has a higher chance to catch a shiny Pokemon.","sprite_name":"ultra_cherish_ball","category":"ball","tmType":null,"amount":2},"rewardPokemon":null,"endDate":"13 hours and 34 minutes"},{"name":"[EVENT] Catch fighting type Pokemon!","goal":30,"progress":5,"rewardItem":null,"rewardPokemon":{"id":903,"name":"Sneasler","description":"Because of Sneasler's virulent poison and daunting physical prowess, no other species could hope to best it on the frozen highlands. Preferring solitude, this species does not form packs.","sprite_name":"sneasler"},"endDate":"6 days, 13 hours and 34 minutes"},{"name":"???","goal":5,"progress":1,"rewardItem":null,"rewardPokemon":{"id":795,"name":"Pheromosa","description":"Although it’s alien to this world and a danger here, it’s apparently a common organism in the world where it normally lives.","sprite_name":"pheromosa"},"endDate":"6 days, 13 hours and 34 minutes"},{"name":"[EVENT] Catch normal type Pokemon!","goal":10,"progress":117,"rewardItem":null,"rewardPokemon":{"id":143,"name":"Snorlax","description":"This Pokémon’s stomach is so strong, even eating moldy or rotten food will not affect it.","sprite_name":"snorlax"},"endDate":"6 days, 13 hours and 34 minutes"},{"name":"Miss catches","goal":15,"progress":15,"rewardItem":{"id":78,"name":"Flying Stone","description":"A stone that makes certain species of Pokémon evolve. It is said that the stone's color determines the Pokémon that will evolve.","sprite_name":"flying_stone","category":"evolution","tmType":null,"amount":1},"rewardPokemon":null,"endDate":"6 days, 13 hours and 34 minutes"},{"name":"Participate in public battles using fighting type","goal":10,"progress":9,"rewardItem":{"id":54,"name":"Total Reset","description":"Total Reset used to teach your Pokémon a full new move set, completely changes the nature of your pokemon and changes the individual values of a Pokémon. Use it with caution.","sprite_name":"total_reset","category":"battle","tmType":null,"amount":1},"rewardPokemon":null,"endDate":"6 days, 13 hours and 34 minutes"},{"name":"Wondertrade dragon type Pokemon","goal":7,"progress":0,"rewardItem":null,"rewardPokemon":{"id":390,"name":"Chimchar","description":"The gas made in its belly burns from its rear end. The fire burns weakly when it feels sick.","sprite_name":"chimchar"},"endDate":"6 days, 13 hours and 34 minutes"},{"name":"Attempt catches","goal":25,"progress":32,"rewardItem":{"id":108,"name":"Nest Ball","description":"A somewhat different Poké Ball that is more effective when used on a Pokémon that can evolve twice.","sprite_name":"nest_ball","category":"ball","tmType":null,"amount":5},"rewardPokemon":null,"endDate":"6 days, 13 hours and 34 minutes"},{"name":"Wonder trade Pokemon over 500 BST","goal":4,"progress":3,"rewardItem":{"id":110,"name":"Level Ball","description":"A special ball that guarantees a Pokemon to have a high enough level to be evolved immediately!","sprite_name":"level_ball","category":"ball","tmType":null,"amount":3},"rewardPokemon":null,"endDate":"6 days, 13 hours and 34 minutes"},{"name":"[EVENT] Catch normal type Pokemon!","goal":20,"progress":117,"rewardItem":null,"rewardPokemon":{"id":10465,"name":"Sawsbuck","description":"They migrate according to the seasons, so some people call Sawsbuck the harbingers of spring.","sprite_name":"sawsbuck-summer"},"endDate":"6 days, 13 hours and 34 minutes"},{"name":"[EVENT] Catch dragon type Pokemon!","goal":10,"progress":48,"rewardItem":null,"rewardPokemon":{"id":612,"name":"Haxorus","description":"While usually kindhearted, it can be terrifying if angered. Tusks that can slice through steel beams are how Haxorus deals with its adversaries.","sprite_name":"haxorus"},"endDate":"6 days, 13 hours and 34 minutes"},{"name":"[EVENT] Catch normal type Pokemon!","goal":40,"progress":117,"rewardItem":null,"rewardPokemon":{"id":773,"name":"Silvally","description":"Having been awakened successfully, it can change its type and battle—just like a certain Pokémon depicted in legends. This is its normal type form.","sprite_name":"silvally"},"endDate":"6 days, 13 hours and 34 minutes"},{"name":"[EVENT] Catch dragon type Pokemon!","goal":20,"progress":48,"rewardItem":null,"rewardPokemon":{"id":86318,"name":"His Goodra","description":"Able to freely control the hardness of its metallic shell. It loathes solitude and is extremely clingy—it will fume and run riot if those dearest to it ever leave its side.","sprite_name":"hisuian-goodra"},"endDate":"6 days, 13 hours and 34 minutes"},{"name":"[EVENT] Catch dragon type Pokemon!","goal":40,"progress":48,"rewardItem":null,"rewardPokemon":{"id":10474,"name":"Silvally","description":"Having been awakened successfully, it can change its type and battle—just like a certain Pokémon depicted in legends. This is its dragon type form.","sprite_name":"silvally-dragon"},"endDate":"6 days, 13 hours and 34 minutes"},{"name":"[EVENT] Catch dragon or normal type Pokemon!","goal":50,"progress":164,"rewardItem":null,"rewardPokemon":{"id":483,"name":"Dialga","description":"It has the power to control time. It appears in Sinnoh-region myths as an ancient deity.","sprite_name":"dialga"},"endDate":"6 days, 13 hours and 34 minutes"},{"name":"Win Challenge","goal":13,"progress":38,"rewardItem":null,"rewardPokemon":{"id":486,"name":"Regigigas","description":"There is an enduring legend that states this Pokémon towed continents with ropes.","sprite_name":"regigigas"},"endDate":"6 days, 13 hours and 34 minutes"},{"name":"[EVENT] Catch fighting type Pokemon!","goal":15,"progress":5,"rewardItem":null,"rewardPokemon":{"id":448,"name":"Lucario","description":"It can tell what people are thinking. Only Trainers who have justice in their hearts can earn this Pokémon’s trust.","sprite_name":"lucario"},"endDate":"6 days, 13 hours and 34 minutes"}],"endDate":"13 hours and 34 minutes"}"""
MISSIONS_STR_9 = """{"missions":[{"name":"Wondertrade Pokémon with less than 362 BST","goal":7,"progress":0,"rewardItem":{"id":97,"name":"Stone Ball","description":"A rare  ball with an increased chance to drop an evolution stone.","sprite_name":"stone_ball","category":"ball","tmType":null,"amount":5},"rewardPokemon":null,"endDate":"6 days, 23 hours and 50 minutes"},{"name":"Win medium stadium battles","goal":10,"progress":0,"rewardItem":null,"rewardPokemon":{"id":86321,"name":"His Voltorb","description":"An enigmatic Pokémon that happens to bear a resemblance to a Poké Ball. When excited, it discharges the electric current it has stored in its belly, then lets out a great, uproarious laugh.","sprite_name":"hisuian-voltorb"},"endDate":"6 days, 23 hours and 50 minutes"},{"name":"Catch rock type Pokémon","goal":7,"progress":0,"rewardItem":{"id":46,"name":"Battle Coin","description":"Reward for joining a PCG tournament. This token can be spend on various rare items and Pokémon in the battle coin shop or kept as reminiscence.","sprite_name":"battle_coin","category":"collectable","tmType":null,"amount":1},"rewardPokemon":null,"endDate":"6 days, 23 hours and 50 minutes"},{"name":"Catch monotype Pokemon","goal":10,"progress":0,"rewardItem":{"id":42,"name":"Empty Disc","description":"An empty disc used to teach your Pokémon a full new move set. Use it with caution.","sprite_name":"empty_disc","category":"battle","tmType":null,"amount":2},"rewardPokemon":null,"endDate":"6 days, 23 hours and 50 minutes"},{"name":"Miss grass type Pokémon","goal":6,"progress":0,"rewardItem":{"id":76,"name":"Normal Stone","description":"A stone that makes certain species of Pokémon evolve. It is said that the stone's color determines the Pokémon that will evolve.","sprite_name":"normal_stone","category":"evolution","tmType":null,"amount":1},"rewardPokemon":null,"endDate":"6 days, 23 hours and 50 minutes"}],"endDate":"6 days, 23 hours and 50 minutes"}"""
MISSIONS_STR_10 = """{"missions":[{"name":"Catch bug type Pokemon","goal":6,"progress":0,"rewardItem":{"id":82,"name":"Bug Stone","description":"A stone that makes certain species of Pokémon evolve. It is said that the stone's color determines the Pokémon that will evolve.","sprite_name":"bug_stone","category":"evolution","tmType":null,"amount":1},"rewardPokemon":null,"endDate":"6 days, 23 hours and 51 minutes"},{"name":"Wonder trade fire type Pokémon","goal":8,"progress":1,"rewardItem":{"id":25,"name":"Timer Ball","description":"A somewhat different Poké Ball that becomes progressively more effective at catching Pokémon the closer the Pokémon is to escaping.","sprite_name":"timer_ball","category":"ball","tmType":null,"amount":4},"rewardPokemon":null,"endDate":"6 days, 23 hours and 51 minutes"},{"name":"Use super effective moves","goal":75,"progress":3,"rewardItem":{"id":46,"name":"Battle Coin","description":"Reward for joining a PCG tournament. This token can be spend on various rare items and Pokémon in the battle coin shop or kept as reminiscence.","sprite_name":"battle_coin","category":"collectable","tmType":null,"amount":1},"rewardPokemon":null,"endDate":"6 days, 23 hours and 51 minutes"},{"name":"Miss catches","goal":30,"progress":1,"rewardItem":null,"rewardPokemon":{"id":10300,"name":"Cherrim","description":"The faint scent that emanates from its full blossom entices bug Pokémon to it.","sprite_name":"cherrim-sunshine"},"endDate":"6 days, 23 hours and 51 minutes"},{"name":"Win easy stadium battles","goal":5,"progress":0,"rewardItem":{"id":45,"name":"Mood Mint","description":"Delicious mint, which completly changes the nature of your pokemon.","sprite_name":"mood_mint","category":"battle","tmType":null,"amount":1},"rewardPokemon":null,"endDate":"6 days, 23 hours and 51 minutes"}],"endDate":"6 days, 23 hours and 51 minutes"}"""
MISSIONS_STR_11 = """{"missions":[{"name":"Wondertrade with a level higher than 13","goal":14,"progress":1,"rewardItem":{"id":27,"name":"Cipher Ball","description":"A somewhat different Poké Ball that is more effective when attempting to catch Poison- or Psychic-type Pokémon.","sprite_name":"cipher_ball","category":"ball","tmType":null,"amount":6},"rewardPokemon":null,"endDate":"6 days, 16 hours and 21 minutes"},{"name":"Miss a catch","goal":30,"progress":23,"rewardItem":null,"rewardPokemon":{"id":10505,"name":"Torchic","description":"Torchic has a place inside its body where it keeps its flame. Give it a hug—it will be glowing with warmth. This Pokémon is covered all over by a fluffy coat of down.","sprite_name":"torchic-f"},"endDate":"6 days, 16 hours and 21 minutes"},{"name":"Participate in a public battle using dark type","goal":14,"progress":45,"rewardItem":{"id":92,"name":"Dark Stone","description":"A stone that makes certain species of Pokémon evolve. It is said that the stone's color determines the Pokémon that will evolve.","sprite_name":"dark_stone","category":"evolution","tmType":null,"amount":1},"rewardPokemon":null,"endDate":"6 days, 16 hours and 21 minutes"},{"name":"Win hard stadium battles","goal":3,"progress":6,"rewardItem":null,"rewardPokemon":{"id":86322,"name":"His Growlithe","description":"They patrol their territory in pairs. I believe the igneous rock components in the fur of this species are the result of volcanic activity in its habitat.","sprite_name":"hisuian-growlithe"},"endDate":"6 days, 16 hours and 21 minutes"},{"name":"Miss ice type Pokemon","goal":5,"progress":0,"rewardItem":{"id":43,"name":"IV Reset","description":"Completely changes the individual values of a Pokémon.","sprite_name":"iv_reset","category":"battle","tmType":null,"amount":1},"rewardPokemon":null,"endDate":"6 days, 16 hours and 21 minutes"}],"endDate":"6 days, 16 hours and 21 minutes"}"""

MISSIONS_JSON = json.loads(MISSIONS_STR)
MISSIONS_JSON_2 = json.loads(MISSIONS_STR_2)
MISSIONS_JSON_3 = json.loads(MISSIONS_STR_3)
MISSIONS_JSON_4 = json.loads(MISSIONS_STR_4)
MISSIONS_JSON_5 = json.loads(MISSIONS_STR_5)
MISSIONS_JSON_6 = {"missions": [{"name": "Use super effective moves", "goal": 75, "progress": 0, "rewardItem": {"id": 42, "name": "Empty Disc", "description": "An empty disc used to teach your Pokémon a full new move set. Use it with caution.", "sprite_name": "empty_disc", "category": "battle", "tmType": None, "amount": 6}, "rewardPokemon": None, "endDate": "6 days,  16 hours and 34 minutes"}, {"name": "Catch fire type pokemon", "goal": 5, "progress": 0, "rewardItem": None, "rewardPokemon": {"id": 100007, "name": "Sin Ninetales", "description": "While it will guide travelers who get lost on a snowy mountain down to the mountain’s base,  it won’t forgive anyone who harms nature.", "sprite_name": "sinister-ninetales"}, "endDate": "6 days,  16 hours and 34 minutes"}, {"name": "Attempt catches", "goal": 30, "progress": 29, "rewardItem": {"id": 97, "name": "Stone Ball", "description": "A rare  ball with an increased chance to drop an evolution stone.", "sprite_name": "stone_ball", "category": "ball", "tmType": None, "amount": 4}, "rewardPokemon": None, "endDate": "6 days,  16 hours and 34 minutes"}, {"name": "Participate in ranked battles", "goal": 5, "progress": 0, "rewardItem": {"id": 46, "name": "Battle Coin", "description": "Reward for joining a PCG tournament. This token can be spend on various rare items and Pokémon in the battle coin shop or kept as reminiscence.", "sprite_name": "battle_coin", "category": "collectable", "tmType": None, "amount": 1}, "rewardPokemon": None, "endDate": "6 days,  16 hours and 34 minutes"}, {"name": "Wonder trade Pokemon over 500 BST", "goal": 7, "progress": 3, "rewardItem": {"id": 44, "name": "Wonder Pass", "description": "A rare pass that permits you to wonder trade again instantly.", "sprite_name": "wonder_pass", "category": "extra", "tmType": None, "amount": 3}, "rewardPokemon": None, "endDate": "6 days,  16 hours and 34 minutes"}, {"name": "Use field effects in battles", "goal": 5, "progress": 0, "rewardItem": {"id": 45, "name": "Mood Mint", "description": "Delicious mint,  which completly changes the nature of your pokemon.", "sprite_name": "mood_mint", "category": "battle", "tmType": None, "amount": 4}, "rewardPokemon": None, "endDate": "6 days,  16 hours and 34 minutes"}, {"name": "Miss fighting catches", "goal": 7, "progress": 1, "rewardItem": {"id": 77, "name": "Fighting Stone", "description": "A stone that makes certain species of Pokémon evolve. It is said that the stone's color determines the Pokémon that will evolve.", "sprite_name": "fighting_stone", "category": "evolution", "tmType": None, "amount": 1}, "rewardPokemon": None, "endDate": "6 days,  16 hours and 34 minutes"}, {"name": "Play stadium battles", "goal": 10, "progress": 0, "rewardItem": {"id": 43, "name": "IV Reset", "description": "Completely changes the individual values of a Pokémon.", "sprite_name": "iv_reset", "category": "battle", "tmType": None, "amount": 4}, "rewardPokemon": None, "endDate": "6 days,  16 hours and 34 minutes"}], "endDate": "6 days,  16 hours and 34 minutes"}
MISSIONS_JSON_7 = json.loads(MISSIONS_STR_7)
MISSIONS_JSON_8 = json.loads(MISSIONS_STR_8)
MISSIONS_JSON_9 = json.loads(MISSIONS_STR_9)
MISSIONS_JSON_10 = json.loads(MISSIONS_STR_10)
MISSIONS_JSON_11 = json.loads(MISSIONS_STR_11)


def test_check_missions_case1():
    MISSIONS.set(MISSIONS_JSON)
    pokemon = Pokemon()
    pokemon.types = ["Normal", "Fairy"]
    reasons = MISSIONS.check_all_missions(pokemon)
    wondertrade_reasons = MISSIONS.check_all_wondertrade_missions(pokemon)

    assert len(reasons) == 1
    assert len(wondertrade_reasons) == 1
    assert "miss" in reasons
    assert "type" in wondertrade_reasons
    assert MISSIONS.have_wondertrade_missions()


def test_check_missions_completed():
    MISSIONS.set(MISSIONS_JSON)
    tmp_missions = {"missions": []}
    mission_title = "Wondertrade normal types"

    for mission in MISSIONS_JSON["missions"]:
        if mission["name"] == mission_title:
            mission_goal = mission["goal"]
            mission["progress"] = mission_goal
            reward = mission["rewardItem"]["name"]
            reward_amount = mission["rewardItem"]["amount"]
        tmp_missions["missions"].append(mission)

    MISSIONS.set(tmp_missions)

    completed = MISSIONS.get_completed()
    assert len(completed) == 1
    assert completed[0][0] == f"{mission_title} ({mission_goal})"
    assert completed[0][1]["reward"] == f"{reward_amount} {reward}"


def test_check_missions_case2():
    MISSIONS.set(MISSIONS_JSON_2)
    pokemon = Pokemon()
    pokemon.types = ["Fire", "Fairy"]
    pokemon.hp = 200
    reasons = MISSIONS.check_all_missions(pokemon)
    wondertrade_reasons = MISSIONS.check_all_wondertrade_missions(pokemon)

    assert len(reasons) == 1
    assert len(wondertrade_reasons) == 1
    assert "type" in reasons
    assert "bst" in wondertrade_reasons

    pokemon = Pokemon()
    pokemon.types = ["Fairy"]
    pokemon.hp = 900
    reasons = MISSIONS.check_all_missions(pokemon)
    wondertrade_reasons = MISSIONS.check_all_wondertrade_missions(pokemon)

    assert len(reasons) == 0
    assert len(wondertrade_reasons) == 0
    assert MISSIONS.have_wondertrade_missions()


def test_check_missions_case3():
    MISSIONS.set(MISSIONS_JSON_3)
    pokemon = Pokemon()
    pokemon.types = ["Ghost", "Ground"]
    pokemon.weight = 300
    reasons = MISSIONS.check_all_missions(pokemon)
    wondertrade_reasons = MISSIONS.check_all_wondertrade_missions(pokemon)

    assert len(reasons) == 2
    assert len(wondertrade_reasons) == 1
    assert "type" in reasons
    assert "weight" in reasons
    assert "type" in wondertrade_reasons


def test_check_missions_case4():
    MISSIONS.set(MISSIONS_JSON_4)
    missions = MISSIONS.data
    assert len(missions.keys()) == 4
    assert len(missions.get("bst", [])) == 1
    assert missions.get("bst", [(0, 0)])[0] == (0, 333)
    assert len(missions.get("type", [])) == 1
    assert missions.get("type", ["none"])[0] == "Psychic"
    assert missions.get("attempt", False) == True
    assert missions.get("miss", False) == True


def test_check_missions_case5_fish():
    MISSIONS.set(MISSIONS_JSON_5)
    missions = MISSIONS.data
    assert missions.get("fish", False) == True
    assert missions.get("weight", [(0, 0)])[0] == (250, 9999)


def test_check_missions_case6():
    MISSIONS.set(MISSIONS_JSON_6)
    missions = MISSIONS.data
    assert missions.get("miss", False) == False
    assert missions.get("attempt", False) == True
    assert missions.get("miss_type", []) == ["Fighting"]


def test_check_missions_case7():
    MISSIONS.set(MISSIONS_JSON_7)
    missions = MISSIONS.data

    wondertrade_bst = missions.get("wondertrade_bst", [])
    assert len(wondertrade_bst) == 1
    assert wondertrade_bst[0] == (500, 9999)
    assert "Fire" in missions.get("type", [])
    assert missions.get("attempt", False)
    assert "Fighting" in missions.get("miss_type", [])
    assert "Dragon" in missions.get("type", [])
    assert "Normal" in missions.get("type", [])


def test_check_missions_case8():
    MISSIONS.set(MISSIONS_JSON_8)
    missions = MISSIONS.data

    wondertrade_bst = missions.get("wondertrade_bst", [])
    assert len(wondertrade_bst) == 1
    assert wondertrade_bst[0] == (500, 9999)
    assert "Dragon" in missions.get("wondertrade_type", [])

    pokemon = Pokemon()

    pokemon.types = ["Ghost", "Dragon"]
    pokemon.hp = 700

    reasons = MISSIONS.check_all_wondertrade_missions(pokemon)
    assert len(reasons) == 2
    assert "type" in reasons
    assert "bst" in reasons
    assert MISSIONS.have_wondertrade_missions()


def test_check_missions_case9():
    MISSIONS.set(MISSIONS_JSON_9)
    missions = MISSIONS.data

    wondertrade_bst = missions.get("wondertrade_bst", [])
    assert len(wondertrade_bst) == 1
    assert wondertrade_bst[0] == (0, 362)

    catch_type = missions.get("type", [])
    assert "Rock" in catch_type
    assert len(catch_type) == 1

    miss_type = missions.get("miss_type", [])
    assert "Grass" in miss_type
    assert len(miss_type) == 1

    assert missions.get("monotype", False)

    pokemon = Pokemon()
    pokemon.types = ["Rock", "Dragon"]
    reasons = MISSIONS.check_all_missions(pokemon)
    assert "type" in reasons
    assert "monotype" not in reasons

    reasons = MISSIONS.check_all_wondertrade_missions(pokemon)
    assert "bst" in reasons

    pokemon = Pokemon()
    pokemon.types = ["Grass"]
    reasons = MISSIONS.check_all_missions(pokemon)
    assert "monotype" in reasons
    assert "miss_type" in reasons

    assert missions.get("stadium", "") == "medium"
    assert MISSIONS.check_stadium_mission()
    assert MISSIONS.check_stadium_difficulty() == "medium"


def test_check_missions_case10():
    MISSIONS.set(MISSIONS_JSON_10)
    missions = MISSIONS.data

    assert missions.get("stadium", "") == "easy"
    assert MISSIONS.check_stadium_mission()
    assert MISSIONS.check_stadium_difficulty() == "easy"

    catch_type = missions.get("type", [])
    assert "Bug" in catch_type
    assert len(catch_type) == 1

    wondertrade_type = missions.get("wondertrade_type", [])
    print("here", wondertrade_type, "here")
    assert "Fire" in wondertrade_type
    assert len(wondertrade_type) == 1


def test_check_missions_case11():
    MISSIONS.set(MISSIONS_JSON_11)
    missions = MISSIONS.data

    assert MISSIONS.have_wondertrade_missions()
    assert MISSIONS.have_mission("wondertrade_level")

    wondertrade_level = missions.get("wondertrade_level", [])
    assert len(wondertrade_level) == 1
    assert wondertrade_level[0] == (13, 9999)

    pokemon = Pokemon()
    pokemon.types = ["Rock", "Dragon"]
    pokemon.level = 15
    reasons = MISSIONS.check_all_wondertrade_missions(pokemon)
    assert "level" in reasons

    pokemon.level = 5

    reasons = MISSIONS.check_all_wondertrade_missions(pokemon)
    assert "level" not in reasons
