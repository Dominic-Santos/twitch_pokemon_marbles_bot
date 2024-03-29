from datetime import datetime
from time import sleep
import random
import copy
from dateutil.parser import parse

from .ChatO import ClientIRC as ClientIRCO
from .ChatO import ChatPresence as ChatPresenceO
from .ChatO import ThreadChat as ThreadChatO

from .ChatThreads import ChatThreads
from .ChatLogs import log, log_file
from .ChatUtils import (
    CHARACTERS,
    ITEM_MIN_AMOUNT,
    ITEM_MIN_PURCHASE,
    MARBLES_DELAY,
    MARBLES_TRIGGER_COUNT,
    POKEMON,
    DISCORD_ALERTS,
    THREADCONTROLLER
)

from .entities.Pokemon import CGApi, get_sprite

MAX_UPDATES = 250


class ClientIRCBase(ClientIRCO):
    def __init__(self, username, token, channel):
        ClientIRCO.__init__(self, username, token, channel)


class ClientIRCMarbles(ClientIRCBase):
    def __init__(self, username, token, channel, marbles):
        ClientIRCBase.__init__(self, username, token, channel)
        self.init(marbles)

    def init(self, marbles):
        self.marbles = marbles
        self.marbles_timer = datetime.utcnow()
        self.marbles_counter = 0

    def on_pubmsg(self, client, message):
        if self.marbles and "!play" in " ".join(message.arguments):
            self.check_marbles(client, message)

    def check_marbles(self, client, message):
        now = datetime.utcnow()
        if (now - self.marbles_timer).total_seconds() > MARBLES_DELAY:
            self.marbles_timer = now
            self.marbles_counter = 0

        self.marbles_counter += 1

        if self.marbles_counter == MARBLES_TRIGGER_COUNT:
            sleep(random.randint(0, 60))
            client.privmsg(message.target, "!play")
            log(text=f"Joined Marbles for {message.target[1:]}")


class ClientIRCPokemon(ClientIRCBase, ChatThreads):
    def __init__(self, username, token, channel, get_pokemon_token, pcg):
        ClientIRCBase.__init__(self, username, token, channel)
        self.init(username, get_pokemon_token, pcg)

    def init(self, username, get_pokemon_token, pcg):
        self.username = username.lower()
        self.at_username = "@" + self.username

        self.pcg = pcg
        self.pokemon_active = False
        self.pokemon_disabled = False
        self.pokemon_api = CGApi()
        self.pokemon_api.get_auth_token = get_pokemon_token

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

            if len(POKEMON.channel_list) > 0:
                self.start_threads()

    def check_snowmen(self, client, message, argstring):
        if argstring.count("❄") == 34:
            try:
                total_score = 0
                for part in ["Hat", "SnowHead", "Cone", "BodyMid", "BowTie"]:
                    if part in argstring:
                        total_score += int(argstring.split(part)[1][0])

                tier = 0
                if total_score == 15:
                    tier = 5
                elif total_score >= 11:
                    tier = 4
                elif total_score == 10:
                    tier = 3
                elif total_score >= 6:
                    tier = 2
                elif total_score == 5:
                    tier = 1

                if tier >= 4:
                    twitch_channel = message.target[1:]
                    log("green", f"A T{tier} snowman has been built in {twitch_channel}")
            except Exception as e:
                log("red", "not a real snowman message - " + argstring + str(e))

    def check_pokegifts(self, client, message, argstring):
        if self.username in argstring.lower() and "as present from" in argstring and "HolidayPresent" in argstring:
            twitch_channel = message.target[1:]
            receiver = argstring.split(" ")[0]
            if self.username not in receiver.lower():
                return

            sender = argstring.split(" ")[-1][1:-1]
            item = argstring.split("HolidayPresent")[1].replace(":", "").strip()

            msg = f"🎁Received {item} as a present from {sender} in {twitch_channel} channel🎁"
            log("green", msg)
            POKEMON.discord.post(DISCORD_ALERTS, msg)

    def check_xmas_delibird_gift(self, client, message, argstring):
        if self.username in argstring.lower() and "Delibird drops the following" in argstring and "HolidayPresent" in argstring:
            twitch_channel = message.target[1:]

            item = argstring.split("HolidayPresent")[1].replace(":", "").strip()
            msg = f"🎁Received {item} as a present from Delibird in {twitch_channel} channel🎁"
            log("green", msg)
            POKEMON.discord.post(DISCORD_ALERTS, msg)

    def check_loyalty_info(self, client, message, argstring):
        if self.username in argstring.lower() and "Your loyalty level" in argstring:
            channel = message.target[1:]
            loyalty_level = int(argstring.split("Your loyalty level: ")[1][0])
            loyalty_limits = argstring.split("(")[1].split(")")[0]
            current_points = int(loyalty_limits.split("/")[0].replace(",", ""))
            level_points = int(loyalty_limits.split("/")[1].replace(",", ""))
            log("yellow", f"{channel} loyalty {current_points}/{level_points}, level {loyalty_level}")

            POKEMON.set_loyalty(channel, loyalty_level, current_points, level_points)

    def check_pokemon_active(self, client, message, argstring):
        if "Spawns and payouts are disabled" in argstring:
            if self.pokemon_disabled is False:
                self.pokemon_disabled = True
                self.pokemon_active = False
                log(text=f"Pokemon Disabled: {self.channel}")
                leave_channel(self.channel[1:])

        elif self.pokemon_active is False:
            if self.pokemon_disabled is False or (" has been caught by:" in argstring or " escaped." in argstring):
                self.pokemon_active = True
                self.pokemon_disabled = False
                log("yellow", f"Joined Pokemon for {message.target[1:]}")
                POKEMON.add_channel(self.channel[1:])

                if POKEMON.need_loyalty(self.channel[1:]):
                    sleep(5)
                    log("yellow", f"{self.channel[1:]} loyalty request")
                    client.privmsg("#" + self.channel[1:], "!pokeloyalty")

    def check_got_dragon_egg(self):
        filtered = sorted(POKEMON.computer.pokemon, key=lambda x: x["id"], reverse=True)[:3]

        caught = None
        pokemon = None
        for poke in filtered:
            pokemon = self.get_pokemon_stats(poke["pokedexId"])
            if pokemon.is_egg is False:
                continue

            if (datetime.utcnow() - parse(poke["caughtAt"][:-1])).total_seconds() > 60 * 5:
                continue

            caught = poke

        return pokemon, caught


    def update_evolutions(self, pokemon_id, pokedex_id):
        pokemon_data = self.pokemon_api.get_pokemon(pokemon_id)
        POKEMON.pokedex.set_evolutions(pokedex_id, pokemon_data["evolutionData"])
        POKEMON.pokedex.save_pokedex()
        return pokemon_data

    def update_inventory(self, skip=False):
        # check if got items from catching or elsewhere
        old_items = copy.deepcopy(POKEMON.inventory.items)
        inv = self.pokemon_api.get_inventory()
        POKEMON.sync_inventory(inv)

        if skip:
            return

        completed_missions = self.get_missions()
        item_rewards = [reward for (_, reward) in completed_missions if reward["reward_type"] != "pokemon"]
        mission_items = {reward["item_name"].lower(): reward["item_amount"] for reward in item_rewards}

        if old_items == {}:
            # skip if init
            return

        for item_name in POKEMON.inventory.items:
            item = POKEMON.inventory.get_item(item_name)
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
            log("green", rewards_msg)
            sprite = get_sprite(item["category"], item["sprite"], tm_type=item["tm_type"])
            POKEMON.discord.post(DISCORD_ALERTS, rewards_msg, file=sprite)

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
            ball_have = POKEMON.inventory.balls.get(ball_name, 0)
            if ball_have < ITEM_MIN_AMOUNT:
                can_afford = POKEMON.inventory.cash // ball["price"] // ITEM_MIN_PURCHASE * ITEM_MIN_PURCHASE
                need = ((ITEM_MIN_AMOUNT - ball_have) // ITEM_MIN_PURCHASE + min((ITEM_MIN_AMOUNT - ball_have) % ITEM_MIN_PURCHASE, 1)) * ITEM_MIN_PURCHASE
                buying = min(need, can_afford)

                if buying > 0:
                    changes = True
                    resp = self.pokemon_api.buy_item(ball["name"], buying)
                    if "cash" in resp:
                        POKEMON.inventory.cash = resp["cash"]
                        log("green", f"Purchased {buying} {ball['displayName']}s")

        if changes:
            inv = self.pokemon_api.get_inventory()
            POKEMON.sync_inventory(inv)

    def get_missions(self):
        missions = self.pokemon_api.get_missions()
        POKEMON.sync_missions(missions)

        completed = POKEMON.missions.get_completed()
        pokemon_to_sort = []
        for title, reward in completed:
            readable_reward = reward["reward"]
            reward_sprite = get_sprite(reward["reward_type"], reward["reward_name"], reward.get("tm_type", None))
            mission_msg = f"Completed mission - {title} - reward:"
            if reward["reward_type"] == "pokemon":

                pokemonobj, caught = self.get_last_caught(reward["reward_name"], reward=True)
                needed = "" if POKEMON.pokedex.have(pokemonobj) else " - needed"
                ivs = int(caught["avgIV"])
                lvl = caught['lvl']
                shiny = " Shiny" if caught["isShiny"] else ""
                mission_msg = f"{mission_msg} {shiny} {pokemonobj.name} ({pokemonobj.tier}) Lvl.{lvl} {ivs}IV{needed}"
                if caught["isShiny"] is False:
                    pokemon_to_sort.append(reward["reward_name"])
            else:
                mission_msg = f"{mission_msg} {readable_reward}"
            log("green", f"{mission_msg}")
            POKEMON.discord.post(DISCORD_ALERTS, mission_msg, file=reward_sprite)
            if reward_sprite is not None:
                reward_sprite.close()

        if len(pokemon_to_sort) > 0:
            self.sort_computer(pokemon_to_sort)
            self.sync_pokemon_data()
        return completed

    def get_last_caught(self, pokedex_id, reward=False):
        pokemon = self.get_pokemon_stats(pokedex_id, cached=False)

        all_pokemon = self.pokemon_api.get_all_pokemon()
        POKEMON.sync_computer(all_pokemon)

        filtered = sorted(POKEMON.computer.pokemon, key=lambda x: x["id"], reverse=True)[:3]

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
            if pokemon.pokedex_id == 999999:
                pokemon.is_unidentified_ghost = True
            else:
                pokemon.is_special_spawn = True

        return pokemon, caught

    def get_pokemon_move(self, move_name, move_type="None"):

        move = POKEMON.pokedex.move(move_name)
        if move is None:
            move_data = self.pokemon_api.get_move(move_name)
            move_data["type"] = move_type

            POKEMON.pokedex.pokemon_moves[str(move_name)] = move_data
            POKEMON.pokedex.save_moves()

            move = POKEMON.pokedex.move(move_name)

        return move

    def get_pokemon_stats(self, pokedex_id, cached=True):

        pokemon = POKEMON.pokedex.stats(str(pokedex_id))

        if cached is False or pokemon is None:
            try:
                pokemon_data = self.pokemon_api.get_pokedex_info(pokedex_id)["content"]
                POKEMON.pokedex.pokemon_stats.setdefault(str(pokedex_id), {}).update(pokemon_data)
                POKEMON.pokedex.save_pokedex()

                pokemon = POKEMON.pokedex.stats(str(pokedex_id))
            except Exception as e:
                print(pokedex_id, "failed to get pokemon stats", e)
                pokemon = None

        return pokemon

    def get_pokemon_data(self, pokemon, cached=True):

        pokemon_data = POKEMON.computer.get_pokemon_data(pokemon["id"])

        if cached is False or pokemon_data is None:
            try:
                resp = self.pokemon_api.get_pokemon(pokemon["id"])
                POKEMON.computer.update_pokemon_data(pokemon, resp)
                POKEMON.computer.save_computer()

                pokemon_data = POKEMON.computer.get_pokemon_data(pokemon["id"])
                log("yellow", f"Updated data for {pokemon['id']} ({pokemon['name']})")
            except Exception as e:
                log("yellow", f"{pokemon['id']} {pokemon['name']} failed to get pokemon data - {str(e)}")
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

    def rename_computer(self, pokedict):
        changes = self.get_rename_suggestion(pokedict)
        for pokemon, new_name in changes:
            if new_name is not None and len(new_name) > 12:
                log_file("yellow", f"Wont rename {pokemon['name']} from {pokemon['nickname']} to {new_name}, name too long")
                continue
            self.pokemon_api.set_name(pokemon['id'], new_name)

            # update data cache
            pokemon_data = self.get_pokemon_data(pokemon)
            pokemon_data["nickname"] = new_name
            POKEMON.computer.set_pokemon_data(pokemon["id"], pokemon_data)

            log_file("yellow", f"Renamed {pokemon['name']} from {pokemon['nickname']} to {new_name}")
            sleep(0.5)

        POKEMON.computer.save_computer()

    def sort_computer(self, pokedex_ids=[]):
        '''Sort all/specific pokemon in computer and rename duplicates'''
        all_pokemon = self.pokemon_api.get_all_pokemon()
        POKEMON.sync_computer(all_pokemon)

        allpokemon = POKEMON.computer.pokemon
        pokedict = {}

        for pokemon in allpokemon:
            if pokemon["isShiny"]:
                continue
            if len(pokedex_ids) == 0 or pokemon["pokedexId"] in pokedex_ids:
                pokedict.setdefault(pokemon["pokedexId"], []).append(pokemon)

        self.rename_computer(pokedict)

    def sync_pokemon_data(self, pokemon_id=None):
        all_pokemon = self.pokemon_api.get_all_pokemon()
        POKEMON.sync_computer(all_pokemon)

        allpokemon = POKEMON.computer.pokemon
        updated = 0

        for pokemon in allpokemon:
            # update computer data if needed
            if updated >= MAX_UPDATES:
                break

            if str(pokemon["id"]) not in POKEMON.computer.pokemon_data:
                updated += 1

            use_cache = pokemon_id != pokemon["id"]

            self.get_pokemon_data(pokemon, cached=use_cache)
            POKEMON.computer.update_pokemon_data(pokemon)

        POKEMON.computer.save_computer()


class ClientIRC(ClientIRCMarbles, ClientIRCPokemon):
    def __init__(self, username, token, channel, get_pokemoncg_token, marbles, pcg):
        ClientIRCMarbles.__init__(self, username, token, channel, marbles)
        ClientIRCPokemon.init(self, username, get_pokemoncg_token, pcg)

    def on_pubmsg(self, client, message):
        ClientIRCMarbles.on_pubmsg(self, client, message)
        ClientIRCPokemon.on_pubmsg(self, client, message)

    def die(self, msg="Bye, cruel world!"):
        ClientIRCPokemon.die(self)
        self.connection.disconnect(msg)
        self.__active = False


class ThreadChat(ThreadChatO):
    def __init__(self, username, token, channel, channel_id, get_pokemoncg_token, marbles, pcg):
        ThreadChatO.__init__(self, username, token, channel)
        self.marbles = marbles
        self.pcg = pcg
        self.channel_id = channel_id
        self.get_pokemoncg_token_func = get_pokemoncg_token

    def get_pokemoncg_token(self):
        return self.get_pokemoncg_token_func(self.channel_id)

    def run(self):
        self.chat_irc = ClientIRC(
            self.username,
            self.token,
            self.channel,
            self.get_pokemoncg_token,
            self.marbles,
            self.pcg
        )
        log(text=f"Join IRC Chat: {self.channel}")
        POKEMON.channel_online(self.channel)
        self.chat_irc.start()

    def stop(self):
        ThreadChatO.stop(self)
        leave_channel(self.channel)


def leave_channel(channel):
    if channel in POKEMON.channel_list:
        POKEMON.remove_channel(channel)
        log(text=f"Leaving Pokemon: {channel}")
        if len(POKEMON.channel_list) == 0:
            log_file(text="Nobody is streaming Pokemon CG")

    if channel in POKEMON.online_channels:
        POKEMON.channel_offline(channel)

    THREADCONTROLLER.remove_client(channel)


ChatPresence = ChatPresenceO
