from datetime import datetime
from time import sleep
import copy
from dateutil.parser import parse

from ..entities.Pokemon import CGApi, get_sprite
from ..ChatO import ClientIRC as ClientIRCO
from ..Utils import (
    CHARACTERS,
    ITEM_MIN_AMOUNT,
    ITEM_MIN_PURCHASE,
    DISCORD_ALERTS,
    THREADCONTROLLER,
    leave_channel,
)

from .ChatThreads import ChatThreads
from .PokemonEvents import PokemonEvents

MAX_UPDATES = 250

class ClientIRCPokemon(ClientIRCO, ChatThreads, PokemonEvents):
    def __init__(self, username, token, channel, get_pokemon_token, pcg, pokemon):
        ClientIRCO.__init__(self, username, token, channel)
        self.init(username, get_pokemon_token, pcg, pokemon)

    def init(self, username, get_pokemon_token, pcg, pokemon):
        self.username = username.lower()
        self.at_username = "@" + self.username

        self.pcg = pcg
        self.pokemon_active = False
        self.pokemon_disabled = False
        self.pokemon_api = CGApi()
        self.pokemon_api.get_auth_token = get_pokemon_token
        self.pokemon = pokemon

    def die(self):
        self.pokemon_active = False
        self.pokemon_disabled = False

    def on_pubmsg(self, client, message):
        if self.pcg:
            argstring = " ".join(message.arguments)

            if "pokemoncommunitygame" in message.source.lower():
                self.check_pokemon_active(client, message, argstring)
                self.check_loyalty_info(client, message, argstring)
                self.check_xmas_delibird_gift(client, message, argstring)
                self.check_pokegifts(client, message, argstring)
                self.check_snowmen(client, message, argstring)

            THREADCONTROLLER.clients[self.channel[1:]] = client

            if len(self.pokemon.channel_list) > 0:
                self.start_threads()

    def check_pokegifts(self, client, message, argstring):
        if self.username in argstring.lower() and "as present from" in argstring and "HolidayPresent" in argstring:
            twitch_channel = message.target[1:]
            receiver = argstring.split(" ")[0]
            if self.username not in receiver.lower():
                return

            sender = argstring.split(" ")[-1][1:-1]
            item = argstring.split("HolidayPresent")[1].replace(":", "").strip()

            msg = f"🎁Received {item} as a present from {sender} in {twitch_channel} channel🎁"
            self.log("green", msg)
            self.pokemon.discord.post(DISCORD_ALERTS, msg)

    def check_loyalty_info(self, client, message, argstring):
        if self.username in argstring.lower() and "Your loyalty level" in argstring:
            channel = message.target[1:]
            loyalty_level = int(argstring.split("Your loyalty level: ")[1][0])
            loyalty_limits = argstring.split("(")[1].split(")")[0]
            current_points = int(loyalty_limits.split("/")[0].replace(",", ""))
            level_points = int(loyalty_limits.split("/")[1].replace(",", ""))
            self.log("yellow", f"{channel} loyalty {current_points}/{level_points}, level {loyalty_level}")

            self.pokemon.set_loyalty(channel, loyalty_level, current_points, level_points)

    def check_pokemon_active(self, client, message, argstring):
        if "Spawns and payouts are disabled" in argstring:
            if self.pokemon_disabled is False:
                self.pokemon_disabled = True
                self.pokemon_active = False
                self.log(text=f"Pokemon Disabled: {self.channel}")
                leave_channel(self.channel[1:])

        elif self.pokemon_active is False:
            if self.pokemon_disabled is False or (" has been caught by:" in argstring or " escaped." in argstring):
                self.pokemon_active = True
                self.pokemon_disabled = False
                self.log("yellow", f"Joined Pokemon for {message.target[1:]}")
                self.pokemon.add_channel(self.channel[1:])

                if self.pokemon.need_loyalty(self.channel[1:]):
                    sleep(5)
                    self.log("yellow", f"{self.channel[1:]} loyalty request")
                    client.privmsg("#" + self.channel[1:], "!pokeloyalty")

    def set_buddy(self, pokemon):
        self.pokemon_api.set_buddy(pokemon["id"])
        msg = f"{pokemon['nickname']} ({pokemon['name']}) was set as buddy!"
        self.log("yellow", msg)
        if self.pokemon.settings["alert_buddy_changed"]:
            self.pokemon.discord.post(DISCORD_ALERTS, msg)

    def update_evolutions(self, pokemon_id, pokedex_id):
        pokemon_data = self.pokemon_api.get_pokemon(pokemon_id)
        self.pokemon.pokedex.set_evolutions(pokedex_id, pokemon_data["evolutionData"])
        self.pokemon.pokedex.save_pokedex()
        return pokemon_data

    def update_inventory(self, skip=False):
        # check if got items from catching or elsewhere
        old_items = copy.deepcopy(self.pokemon.inventory.items)
        inv = self.pokemon_api.get_inventory()
        self.pokemon.sync_inventory(inv)

        if skip:
            return

        completed_missions = self.get_missions()
        item_rewards = [reward for (_, reward) in completed_missions if reward["reward_type"] != "pokemon"]
        mission_items = {reward["item_name"].lower(): reward["item_amount"] for reward in item_rewards}

        if old_items == {}:
            # skip if init
            return

        for item_name in self.pokemon.inventory.items:
            item = self.pokemon.inventory.get_item(item_name)
            old_item = old_items.get(item_name, {"amount": 0})

            amount_got = item["amount"] - old_item["amount"] - mission_items.get(item_name, 0)
            if amount_got < 1:
                continue

            item_str = item["name"]
            if amount_got == 1:
                prefix = "an" if item_name[0] in ["a", "e", "i", "o", "u"] else "a"
            else:
                prefix = amount_got

            rewards_msg = f"You got {prefix} {item_str}!"
            self.log("green", rewards_msg)
            sprite = get_sprite(item["category"], item["sprite"], tm_type=item["tm_type"])
            self.pokemon.discord.post(DISCORD_ALERTS, rewards_msg, file=sprite)

    def check_inventory(self):
        self.update_inventory()

        shop = self.pokemon_api.get_shop()
        shop_balls = []
        for item in shop["shopItems"]:
            if item["category"] == "ball":
                shop_balls.append(item)

        changes = False
        for ball in sorted(shop_balls, key=lambda x: x["price"]):
            ball_name = ball["displayName"].lower().replace(" ", "")
            ball_have = self.pokemon.inventory.balls.get(ball_name, 0)
            if ball_have < ITEM_MIN_AMOUNT:
                can_afford = self.pokemon.inventory.cash // ball["price"] // ITEM_MIN_PURCHASE * ITEM_MIN_PURCHASE
                need = ((ITEM_MIN_AMOUNT - ball_have) // ITEM_MIN_PURCHASE + min((ITEM_MIN_AMOUNT - ball_have) % ITEM_MIN_PURCHASE, 1)) * ITEM_MIN_PURCHASE
                buying = min(need, can_afford)

                if buying > 0:
                    changes = True
                    resp = self.pokemon_api.buy_item(ball["name"], buying)
                    if "cash" in resp:
                        self.pokemon.inventory.cash = resp["cash"]
                        self.log("green", f"Purchased {buying} {ball['displayName']}s")

        if changes:
            inv = self.pokemon_api.get_inventory()
            self.pokemon.sync_inventory(inv)

    def get_missions(self):
        missions = self.pokemon_api.get_missions()
        self.pokemon.sync_missions(missions)

        completed = self.pokemon.missions.get_completed()
        pokemon_to_sort = []
        for title, reward in completed:
            readable_reward = reward["reward"]
            reward_sprite = get_sprite(reward["reward_type"], reward["reward_name"], reward.get("tm_type", None))
            mission_msg = f"Completed mission - {title} - reward:"
            if reward["reward_type"] == "pokemon":

                pokemonobj, caught = self.get_last_caught(reward["reward_name"], reward=True)
                needed = "" if self.pokemon.pokedex.have(pokemonobj) else " - needed"
                ivs = int(caught["avgIV"])
                lvl = caught['lvl']
                shiny = " Shiny" if caught["isShiny"] else ""
                mission_msg = f"{mission_msg} {shiny} {pokemonobj.name} ({pokemonobj.tier}) Lvl.{lvl} {ivs}IV{needed}"
                if caught["isShiny"] is False:
                    pokemon_to_sort.append(reward["reward_name"])
            else:
                mission_msg = f"{mission_msg} {readable_reward}"
            self.log("green", f"{mission_msg}")
            self.pokemon.discord.post(DISCORD_ALERTS, mission_msg, file=reward_sprite)
            if reward_sprite is not None:
                reward_sprite.close()

        if len(pokemon_to_sort) > 0:
            self.sort_computer(pokemon_to_sort)
            self.sync_pokemon_data()
        return completed

    def get_last_caught(self, pokedex_id, reward=False):
        pokemon = self.get_pokemon_stats(pokedex_id, cached=False)

        all_pokemon = self.pokemon_api.get_all_pokemon()
        self.pokemon.sync_computer(all_pokemon)

        filtered = sorted(self.pokemon.computer.pokemon, key=lambda x: x["id"], reverse=True)[:3]

        is_hidden = pokemon.pokedex_id in [999999, 1000000]

        caught = None
        for poke in filtered:
            if poke["pokedexId"] != pokemon.pokedex_id and is_hidden is False:
                continue

            if (datetime.utcnow() - parse(poke["caughtAt"][:-1])).total_seconds() > 60 * 5:
                continue

            poke_info = self.pokemon_api.get_pokemon(poke["id"])
            if (" " in poke_info["originalChannel"] and reward) or (" " not in poke_info["originalChannel"] and reward is False):
                caught = poke
                break

        if caught is not None and pokemon.pokedex_id in [999999, 1000000]:
            pokemon = self.get_pokemon_stats(caught["pokedexId"], cached=False)
            pokemon.is_unidentified_spawn = True

        return pokemon, caught

    def get_pokemon_move(self, move_name, move_type="None"):

        move = self.pokemon.pokedex.move(move_name)
        if move is None:
            move_data = self.pokemon_api.get_move(move_name)
            move_data["type"] = move_type

            self.pokemon.pokedex.pokemon_moves[str(move_name)] = move_data
            self.pokemon.pokedex.save_moves()

            move = self.pokemon.pokedex.move(move_name)

        return move

    def get_pokemon_stats(self, pokedex_id, cached=True):

        pokemon = self.pokemon.pokedex.stats(str(pokedex_id))

        if cached is False or pokemon is None:
            try:
                pokemon_data = self.pokemon_api.get_pokedex_info(pokedex_id)["content"]
                self.pokemon.pokedex.pokemon_stats.setdefault(str(pokedex_id), {}).update(pokemon_data)
                self.pokemon.pokedex.save_pokedex()

                pokemon = self.pokemon.pokedex.stats(str(pokedex_id))
            except Exception as e:
                print(pokedex_id, "failed to get pokemon stats", e)
                pokemon = None

        return pokemon

    def get_pokemon_data(self, pokemon, cached=True):

        pokemon_data = self.pokemon.computer.get_pokemon_data(pokemon["id"])

        if cached is False or pokemon_data is None:
            try:
                resp = self.pokemon_api.get_pokemon(pokemon["id"])
                self.pokemon.computer.update_pokemon_data(pokemon, resp)
                self.pokemon.computer.save_computer()

                pokemon_data = self.pokemon.computer.get_pokemon_data(pokemon["id"])
                self.log("yellow", f"Updated data for {pokemon['id']} ({pokemon['name']})")
            except Exception as e:
                self.log("yellow", f"{pokemon['id']} {pokemon['name']} failed to get pokemon data - {str(e)}")
                pokemon_data = None

        return pokemon_data

    def get_rename_suggestion(self, pokedict):
        changes = []
        for pokeid in pokedict.keys():
            ordered = sorted(pokedict[pokeid], key=lambda x: (-x["avgIV"], -x["sellPrice"], -x["lvl"], -x["id"]))
            for index, pokemon in enumerate(ordered):
                if pokemon["nickname"] is not None:
                    if "trade" not in pokemon["nickname"]:
                        tempnick = pokemon["nickname"]
                        for character in CHARACTERS.values():
                            tempnick = tempnick.replace(character, "")
                        if tempnick != pokemon["name"]:
                            continue

                pokemon_obj = self.get_pokemon_stats(pokemon["pokedexId"])
                
                if pokemon_obj.is_egg:
                    continue

                if index == 0:
                    nick = ""
                    if pokemon_obj.is_starter or pokemon_obj.is_legendary or pokemon_obj.is_female:
                        nick = pokemon["name"]
                        if pokemon_obj.is_starter:
                            nick = CHARACTERS["starter"] + nick
                        if pokemon_obj.is_legendary:
                            nick = CHARACTERS["legendary"] + nick
                        if pokemon_obj.is_female:
                            nick = nick + CHARACTERS["female"]
                    elif pokemon["nickname"] is None:
                        continue
                else:

                    nick = "trade" + pokemon_obj.tier
                    if pokemon_obj.is_starter:
                        nick = CHARACTERS["starter"] + nick
                    if pokemon_obj.is_legendary:
                        nick = CHARACTERS["legendary"] + nick
                    if pokemon_obj.is_female:
                        nick = nick + CHARACTERS["female"]

                if pokemon["nickname"] == nick:
                    continue
                changes.append((pokemon, nick))
        return changes

    def rename_computer(self, changes):
        for pokemon, new_name in changes:
            if new_name is not None and len(new_name) > 12:
                self.log_file("yellow", f"Wont rename {pokemon['name']} from {pokemon['nickname']} to {new_name}, name too long")
                continue
            self.pokemon_api.set_name(pokemon['id'], new_name)

            # update data cache
            pokemon_data = self.get_pokemon_data(pokemon)
            pokemon_data["nickname"] = new_name
            self.pokemon.computer.set_pokemon_data(pokemon["id"], pokemon_data)

            self.log_file("yellow", f"Renamed {pokemon['name']} from {pokemon['nickname']} to {new_name}")
            sleep(0.5)

    def sort_computer_by_pokedex_id(self, pokedex_ids=[]):
        allpokemon = self.pokemon.computer.pokemon
        pokedict = {}

        for pokemon in allpokemon:
            if pokemon["isShiny"]:
                continue
            if len(pokedex_ids) == 0 or pokemon["pokedexId"] in pokedex_ids:
                pokedict.setdefault(pokemon["pokedexId"], []).append(pokemon)
        return pokedict

    def sort_computer(self, pokedex_ids=[]):
        '''Sort all/specific pokemon in computer and rename duplicates'''
        all_pokemon = self.pokemon_api.get_all_pokemon()
        self.pokemon.sync_computer(all_pokemon)

        pokedict = self.sort_computer_by_pokedex_id()
        changes = self.get_rename_suggestion(pokedict)

        self.rename_computer(changes)
        self.pokemon.computer.save_computer()

    def sync_pokemon_data(self, pokemon_id=None):
        all_pokemon = self.pokemon_api.get_all_pokemon()
        self.pokemon.sync_computer(all_pokemon)

        allpokemon = self.pokemon.computer.pokemon
        updated = 0

        for pokemon in allpokemon:
            # update computer data if needed
            if updated >= MAX_UPDATES:
                break

            if str(pokemon["id"]) not in self.pokemon.computer.pokemon_data:
                updated += 1

            use_cache = pokemon_id != pokemon["id"]

            self.get_pokemon_data(pokemon, cached=use_cache)
            self.pokemon.computer.update_pokemon_data(pokemon)

        self.pokemon.computer.save_computer()
