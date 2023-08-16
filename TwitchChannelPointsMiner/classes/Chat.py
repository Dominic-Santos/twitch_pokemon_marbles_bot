from datetime import datetime, timedelta
from time import sleep
from dateutil.parser import parse
import random
import logging
from threading import Thread
import traceback
import requests
import os
import copy

from .ChatO import ClientIRC as ClientIRCO
from .ChatO import ChatPresence as ChatPresenceO
from .ChatO import ThreadChat as ThreadChatO
from .ChatO import logger

from .entities.Pokemon import PokemonComunityGame, CGApi, Pokedaily, get_sprite, Battle, damage_calculator
from .entities.Pokemon.Pokedex import Move

if os.path.exists("logs") is False:
    os.makedirs("logs")

LOGFILE = "logs/pokemoncg.txt"

formatter = logging.Formatter('%(asctime)s %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
file_handler = logging.FileHandler(LOGFILE, encoding='utf-8')
file_handler.setFormatter(formatter)
poke_logger = logging.getLogger(__name__ + "pokemon")
poke_logger.setLevel(logging.DEBUG)
poke_logger.addHandler(file_handler)

ITEM_MIN_AMOUNT = 10
ITEM_MIN_PURCHASE = 10

MARBLES_DELAY = 60 * 3  # seconds
MARBLES_TRIGGER_COUNT = 3

REDLOG = "\x1b[31;20m"
GREENLOG = "\x1b[32;20m"
YELLOWLOG = "\x1b[36;20m"

ALERTS_CHANNEL = 1072557550526013440
STATS_CHANNEL = 1137163122063450162
POKEDAILY_CHANNEL = 800433942695247872
POKEDAILY_GUILD = 711921837503938640

POKEMON = PokemonComunityGame()

DISCORD_BASE = "https://discord.com/api/v9/"
DISCORD_ALERTS = f"{DISCORD_BASE}channels/{ALERTS_CHANNEL}/messages"
DISCORD_STATS = f"{DISCORD_BASE}channels/{STATS_CHANNEL}/messages"
DISCORD_POKEDAILY = f"{DISCORD_BASE}channels/{POKEDAILY_CHANNEL}/messages"
DISCORD_POKEDAILY_SEARCH = f"{DISCORD_BASE}guilds/{POKEDAILY_GUILD}/messages/search?channel_id={POKEDAILY_CHANNEL}&mentions=" + "{discord_id}"

FISH_EVENT = False


class ThreadController(object):
    def __init__(self):
        self.client_channel = None
        self.clients = {}
        self.wondertrade = False
        self.pokecatch = False
        self.pokedaily = False
        self.bag_stats = False
        self.battle = False

    def remove_client(self, channel):
        self.clients.pop(channel, None)
        if self.client_channel == channel:
            self.client_channel = None

    def chose_client(self):
        client_keys = list(self.clients.keys())
        if len(client_keys) > 0:
            self.client_channel = client_keys[0]

    def get_client(self):
        if self.client_channel is None:
            self.chose_client()

        return self.client_channel, self.clients.get(self.client_channel, None)


THREADCONTROLLER = ThreadController()

CHARACTERS = {
    "starter": "⭐",
    "female": "♀",
    "legendary": "💪"
}


def seconds_readable(seconds):
    return str(timedelta(seconds=seconds)).split(".")[0]


def create_thread(func):
    worker = Thread(target=func)
    worker.setDaemon(True)
    worker.start()


def reload_settings():
    while True:
        sleep(60)
        changes = POKEMON.load_settings()
        if changes:
            logger.info(f"{GREENLOG}Settings Reloaded", extra={"emoji": ":speech_balloon:"})


create_thread(reload_settings)


def timer_thread(func):
    def pokemon_timer():

        remaining_human = seconds_readable(POKEMON.delay)
        logger.info(f"{YELLOWLOG}Waiting for {remaining_human}", extra={"emoji": ":speech_balloon:"})
        sleep(POKEMON.delay)

        try:
            client_channel, client = THREADCONTROLLER.get_client()
            if client is not None:
                func(client)

            data = requests.get("https://poketwitch.bframework.de/info/events/last_spawn/").json()
            POKEMON.delay = data["next_spawn"] + 2
        except KeyboardInterrupt:
            return
        except Exception as ex:
            str_ex = str(ex)
            logger.info(f"{REDLOG}Timer func failed - {str_ex}", extra={"emoji": ":speech_balloon:"})
            THREADCONTROLLER.remove_client(client_channel)
            POKEMON.delay = 5
            print(traceback.format_exc())

            if len(POKEMON.channel_list) == 0:
                THREADCONTROLLER.pokecatch = False

        if THREADCONTROLLER.pokecatch:
            create_thread(pokemon_timer)

    if THREADCONTROLLER.pokecatch is False:
        logger.info(f"{YELLOWLOG}Thread Created Spawn Timer", extra={"emoji": ":speech_balloon:"})
        THREADCONTROLLER.pokecatch = True
        try:
            data = requests.get("https://poketwitch.bframework.de/info/events/last_spawn/").json()
            POKEMON.delay = data["next_spawn"] + 2
            create_thread(pokemon_timer)
        except:
            logger.info(f"{REDLOG}Thread Spawn Timer Failed", extra={"emoji": ":speech_balloon:"})
            sleep(10)
            THREADCONTROLLER.pokecatch = False


def wondertrade_thread(func):
    max_wait = 60 * 60  # 1 hour

    def wondertrade_timer():
        if POKEMON.wondertrade_timer is None:
            remaining = 5
        else:
            remaining = POKEMON.check_wondertrade_left().total_seconds()

        remaining_human = seconds_readable(remaining)
        logger.info(f"{YELLOWLOG}Waiting for {remaining_human}", extra={"emoji": ":speech_balloon:"})

        sleep(min(remaining, max_wait))
        if remaining <= max_wait:
            try:
                func()
            except KeyboardInterrupt:
                return
            except Exception as ex:
                str_ex = str(ex)
                logger.info(f"{REDLOG}Wondertrade func failed - {str_ex}", extra={"emoji": ":speech_balloon:"})
                POKEMON.wondertrade_timer = None
                print(traceback.format_exc())

                if len(POKEMON.channel_list) == 0:
                    THREADCONTROLLER.wondertrade = False

        create_thread(wondertrade_timer)

    if THREADCONTROLLER.wondertrade is False:
        logger.info(f"{YELLOWLOG}Thread Created Wondertrade", extra={"emoji": ":speech_balloon:"})
        THREADCONTROLLER.wondertrade = True
        create_thread(wondertrade_timer)


def battle_thread(func):
    def battle_timer():
        try:
            func()
        except KeyboardInterrupt:
            return
        except Exception as ex:
            str_ex = str(ex)
            logger.info(f"{REDLOG}Battle func failed - {str_ex}", extra={"emoji": ":speech_balloon:"})
            print(traceback.format_exc())

            sleep(10)
            if len(POKEMON.channel_list) == 0:
                THREADCONTROLLER.battle = False

        create_thread(battle_timer)

    if THREADCONTROLLER.battle is False:
        logger.info(f"{YELLOWLOG}Thread Created Battle", extra={"emoji": ":speech_balloon:"})
        THREADCONTROLLER.battle = True
        create_thread(battle_timer)


def pokedaily_thread(func):
    max_wait = 60 * 60  # 1 hour

    def pokedaily_timer():
        if POKEMON.pokedaily_timer is None:
            remaining = 5
        else:
            remaining = POKEMON.check_pokedaily_left().total_seconds()

        remaining_human = seconds_readable(remaining)
        logger.info(f"{YELLOWLOG}Waiting for {remaining_human}", extra={"emoji": ":speech_balloon:"})

        sleep(max(min(remaining, max_wait), 1))
        if remaining <= max_wait:
            func()

        create_thread(pokedaily_timer)

    if THREADCONTROLLER.pokedaily is False:
        logger.info(f"{YELLOWLOG}Thread Created Pokedaily", extra={"emoji": ":speech_balloon:"})
        THREADCONTROLLER.pokedaily = True
        create_thread(pokedaily_timer)


def bag_stats_thread(func):
    def bag_stats_timer():
        previous = None
        while True:
            cur_date = datetime.now().date()
            if cur_date != previous:
                logger.info(f"{YELLOWLOG}Running Bag Stats", extra={"emoji": ":speech_balloon:"})
                func(previous, cur_date)
                previous = cur_date
            sleep(60 * 15)  # 15 mins

    if THREADCONTROLLER.bag_stats is False:
        logger.info(f"{YELLOWLOG}Thread Created Bag Stats", extra={"emoji": ":speech_balloon:"})
        THREADCONTROLLER.bag_stats = True
        create_thread(bag_stats_timer)


def get_battle_logs(the_date):
    total_exp = 0
    total_cash = 0
    total_battles = 0
    total_wins = 0

    with open(LOGFILE, mode="rb") as file:
        for uline in file:
            try:
                line = uline.decode("utf-8").rstrip()
            except:
                continue

            if "the battle!" not in line:
                continue

            linedate = parse(line.split(" ")[0])
            if linedate.date() != the_date:
                continue

            rewards = line.split("rewards: ")[1].split(" and ")
            exp = int(rewards[0][:-3])
            cash = int(rewards[1][:-1])

            total_exp += exp
            total_cash += cash
            total_battles += 1
            if "Won" in line:
                total_wins += 1

    return {
        "cash": total_cash,
        "exp": total_exp,
        "battles": total_battles,
        "wins": total_wins,
    }


class ClientIRCBase(ClientIRCO):
    def __init__(self, username, token, channel):
        ClientIRCO.__init__(self, username, token, channel)

    @staticmethod
    def log(msg):
        logger.info(msg, extra={"emoji": ":speech_balloon:"})


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
            self.log(f"Joined Marbles for {message.target[1:]}")


class ClientIRCPokemon(ClientIRCBase):
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

    @staticmethod
    def log_file(msg):
        poke_logger.info(msg)

    def die(self):
        self.pokemon_active = False
        self.pokemon_disabled = False

    def on_pubmsg(self, client, message):
        if self.pcg:
            argstring = " ".join(message.arguments)

            if "pokemoncommunitygame" in message.source:
                self.check_pokemon_active(client, message, argstring)
                self.check_loyalty_info(client, message, argstring)

            THREADCONTROLLER.clients[self.channel[1:]] = client

            if len(POKEMON.channel_list) > 0:
                if THREADCONTROLLER.pokecatch is False:
                    timer_thread(self.check_main)
                if THREADCONTROLLER.wondertrade is False:
                    wondertrade_thread(self.wondertrade_main)
                if THREADCONTROLLER.pokedaily is False:
                    self.pokedaily_setup()
                    pokedaily_thread(self.pokedaily_main)
                if THREADCONTROLLER.bag_stats is False:
                    bag_stats_thread(self.daily_tasks)
                if THREADCONTROLLER.battle is False:
                    battle_thread(self.auto_battle)

    def find_best_move(self, attacker, attacker_moves, defender):
        best_move = None
        # best_move = list(attacker_moves.keys())[0]
        best_damage = -1
        best_move_data = Move("struggle", {
            "name": "Struggle",
            "damage_class": "physical",
            "power": 30,
            "pp": 100,
            "type": "Normal"
        })

        for move_id in attacker_moves:
            move = attacker_moves[move_id]

            if move["pp"] > 0:

                move_data = self.get_pokemon_move(move["id"], move["type"])

                # attacker, move data, defender, weather, attacker burned
                min_damage, max_damage = damage_calculator(attacker, move_data, defender, "normal", False)

                if min_damage > best_damage:
                    best_damage = min_damage
                    best_move = move_id
                    best_move_data = move_data

        return {
            "damage": best_damage,
            "move_id": best_move,
            "move_data": best_move_data
        }

    def matchup_winner(self, my, enemy, switched=False):
        my_pokemon = copy.deepcopy(my)
        enemy_pokemon = copy.deepcopy(enemy)
        my_stats = self.get_pokemon_stats(my_pokemon["pokedex_id"])
        enemy_stats = self.get_pokemon_stats(enemy_pokemon["pokedex_id"])
        skip = switched
        move = None

        # run until one is dead
        while my_pokemon["hp"] > 0 and enemy_pokemon["hp"] > 0:
            my_move = self.find_best_move(my_stats, my_pokemon["moves"], enemy_stats)
            enemy_move = self.find_best_move(enemy_stats, enemy_pokemon["moves"], my_stats)

            if move is None:
                move = my_move

            if my_move["move_id"] is None:
                # attacker, move data, defender, weather, attacker burned
                my_move["damage"] = damage_calculator(my_stats, my_move["move_data"], enemy_stats, "normal", False)[0]
            elif skip is False:
                my_pokemon["moves"][my_move["move_id"]]["pp"] = my_pokemon["moves"][my_move["move_id"]]["pp"] - 1

            if enemy_move["move_id"] is None:
                # attacker, move data, defender, weather, attacker burned
                enemy_move["damage"] = damage_calculator(enemy_stats, my_move["move_data"], my_stats, "normal", False)[0]
            else:
                enemy_pokemon["moves"][enemy_move["move_id"]]["pp"] = enemy_pokemon["moves"][enemy_move["move_id"]]["pp"] - 1

            if my_move["move_data"].priority > enemy_move["move_data"].priority or (
                my_move["move_data"].priority == enemy_move["move_data"].priority and my_stats.speed > enemy_stats.speed
            ):
                # I attack first
                if skip:
                    skip = False
                else:
                    enemy_pokemon["hp"] = enemy_pokemon["hp"] - my_move["damage"]
                    if enemy_pokemon["hp"] <= 0:
                        continue

                my_pokemon["hp"] = my_pokemon["hp"] - enemy_move["damage"]
            else:
                # enemy attacks first
                my_pokemon["hp"] = my_pokemon["hp"] - enemy_move["damage"]
                if my_pokemon["hp"] <= 0:
                    continue

                if skip:
                    skip = False
                else:
                    enemy_pokemon["hp"] = enemy_pokemon["hp"] - my_move["damage"]
        return {
            "win": my_pokemon["hp"] > 0,
            "dealt": enemy["hp"] - enemy_pokemon["hp"],
            "taken": my["hp"] - my_pokemon["hp"],
            "move": "" if move is None else move["move_id"]
        }

    def do_battle(self):
        battle_data = self.pokemon_api.battle_join()
        battle = Battle()
        battle.set_battle(battle_data["battle_id"], battle_data["player_id"], battle_data["unique_battle_key"])
        while battle.state != "end":
            if battle.state == "move":
                # submit a move or switch
                battle.state = "continue"
                pokemon = battle.team["pokemon"][str(battle.team["current_pokemon"])]
                enemy = battle.enemy_team["pokemon"][str(battle.enemy_team["current_pokemon"])]

                result = self.matchup_winner(pokemon, enemy)

                if result["win"]:
                    if result["move"] is None:
                        result["move"] = list(pokemon["moves"].keys())[0]
                    self.pokemon_api.battle_submit_move(battle.battle_id, result["move"])
                    sleep(1)
                    continue

                elif pokemon["hp"] > pokemon["max_hp"] / 2:
                    best_result = None
                    best_switch_id = None
                    for other_pokemon_id in battle.team["pokemon"]:
                        if other_pokemon_id != str(battle.team["current_pokemon"]):
                            other_pokemon = battle.team["pokemon"][other_pokemon_id]
                            if other_pokemon["hp"] > 0:
                                swap = False
                                switch_result = self.matchup_winner(other_pokemon, enemy, True)

                                if best_result is None:
                                    swap = True
                                elif switch_result["win"]:
                                    if switch_result["win"] != best_result["win"]:
                                        swap = True
                                    elif switch_result["win"]:
                                        if switch_result["taken"] < best_result["taken"]:
                                            swap = True
                                    else:
                                        if switch_result["dealt"] > best_result["dealt"]:
                                            swap = True

                                if swap:
                                    best_switch_id = other_pokemon_id
                                    best_result = switch_result

                    if best_result is not None:
                        if best_result["win"]:
                            self.pokemon_api.battle_switch_pokemon(battle.battle_id, best_switch_id)
                            sleep(1)
                            continue

                # battle.submit_move(result["move"])
                self.pokemon_api.battle_submit_move(battle.battle_id, result["move"])
                sleep(1)

            elif battle.state == "switch":
                # pick a pokemon to switch to
                battle.state = "continue"

                enemy = battle.enemy_team["pokemon"][str(battle.enemy_team["current_pokemon"])]
                best_result = None
                best_switch_id = None
                for other_pokemon_id in battle.team["pokemon"]:
                    if other_pokemon_id != str(battle.team["current_pokemon"]):
                        other_pokemon = battle.team["pokemon"][other_pokemon_id]
                        if other_pokemon["hp"] > 0:
                            swap = False
                            switch_result = self.matchup_winner(other_pokemon, enemy, True)

                            if best_result is None:
                                swap = True
                            elif switch_result["win"]:
                                if switch_result["win"] != best_result["win"]:
                                    swap = True
                                elif switch_result["win"]:
                                    if switch_result["taken"] < best_result["taken"]:
                                        swap = True
                                else:
                                    if switch_result["dealt"] > best_result["dealt"]:
                                        swap = True

                            if swap:
                                best_switch_id = other_pokemon_id
                                best_result = switch_result
                if best_result is None:
                    battle.state = "move"
                    continue
                self.pokemon_api.battle_switch_pokemon(battle.battle_id, best_switch_id)
                sleep(1)

            resp = self.pokemon_api.battle_action(battle.action, battle.battle_id, battle.player_id)
            battle.run_action(resp)
            sleep(0.1)

        if battle.result:
            self.log_file(f"{GREENLOG}Won the battle! rewards: {battle.rewards}")
        else:
            self.log_file(f"{REDLOG}Lost the battle! rewards: {battle.rewards}")

        return battle.result, battle_data["unique_battle_key"]

    def auto_battle(self):

        if POKEMON.auto_battle:

            data = self.pokemon_api.get_battle()

            if data["rejoinableBattle"]:
                self.log(f"{YELLOWLOG}Rejoining battle")
                self.do_battle()
                return

            team_data = self.pokemon_api.get_teams()

            battle_mode = "stadium"
            difficulty = "hard"

            if POKEMON.auto_battle_challenge and team_data["challenge"] is not None:
                if team_data["challenge"]["error"] == "" or "Try again in" in team_data["challenge"]["error"]:
                    battle_mode = "challenge"
                    difficulty = "medium"
                else:
                    self.log(f"{REDLOG}Didn't meet requirements for challenge battle, switching to stadium")

            if battle_mode in team_data:

                if team_data[battle_mode]["error"] == "":
                    remaining = 0
                else:
                    try:
                        time_array = team_data[battle_mode]["error"].split("(")[1].split(" ")
                        if len(time_array) == 5:
                            remaining = 60 * int(time_array[0]) + int(time_array[3])
                        elif "minutes" in time_array:
                            remaining = 60 * int(time_array[0])
                        else:
                            remaining = int(time_array[0])
                    except:
                        remaining = 0

                if remaining > 0:
                    remaining_human = seconds_readable(remaining)
                    logger.info(f"{YELLOWLOG}Next {battle_mode} battle in {remaining_human}", extra={"emoji": ":speech_balloon:"})

                sleep(remaining + 1)

                if battle_mode == "stadium":
                    self.get_missions()
                    if POKEMON.missions.check_stadium_mission():
                        difficulty = POKEMON.missions.check_stadium_difficulty()

                team_data = self.pokemon_api.get_teams()
                if team_data[battle_mode]["meet_requirements"]:
                    team_id = team_data["teamNumber"]
                    data = self.pokemon_api.battle_create(battle_mode, difficulty, team_id)
                    battle_message = f"{difficulty} {battle_mode}" if battle_mode == "stadium" else battle_mode
                    self.log(f"{YELLOWLOG}Starting {battle_message} battle")
                    result, key = self.do_battle()
                    if result and battle_mode == "challenge":
                        POKEMON.discord.post(DISCORD_ALERTS, f"⚔️ Won challenge battle {team_data['challenge']['name']} - {key} ⚔️")
                else:
                    self.log(f"{REDLOG}Didn't meet requirements for {battle_mode} battle")
                    sleep(15)
            else:
                self.log(f"{REDLOG}Error: {battle_mode} not in response")
                sleep(15)
        else:
            sleep(30)

    def check_loyalty_info(self, client, message, argstring):
        if self.username in argstring and "Your loyalty level" in argstring:
            channel = message.target[1:]
            loyalty_level = int(argstring.split("Your loyalty level: ")[1][0])
            loyalty_limits = argstring.split("(")[1].split(")")[0]
            current_points = int(loyalty_limits.split("/")[0])
            level_points = int(loyalty_limits.split("/")[1])
            self.log(f"{YELLOWLOG}{channel} loyalty {current_points}/{level_points}, level {loyalty_level}")

            POKEMON.set_loyalty(channel, loyalty_level, current_points, level_points)

    def check_pokemon_active(self, client, message, argstring):
        if "Spawns and payouts are disabled" in argstring:
            if self.pokemon_disabled is False:
                self.pokemon_disabled = True
                self.pokemon_active = False
                logger.info(f"Pokemon Disabled: {self.channel}", extra={"emoji": ":speech_balloon:"})
                leave_channel(self.channel[1:])

        elif self.pokemon_active is False:
            if self.pokemon_disabled is False or (" has been caught by:" in argstring or " escaped." in argstring):
                self.pokemon_active = True
                self.pokemon_disabled = False
                self.log(f"{YELLOWLOG}Joined Pokemon for {message.target[1:]}")
                POKEMON.add_channel(self.channel[1:])

                if self.channel[1:] not in POKEMON.loyalty_data:
                    sleep(5)
                    self.log(f"{YELLOWLOG}{self.channel[1:]} loyalty request")
                    client.privmsg("#" + self.channel[1:], "!pokeloyalty")

    def pokedaily_setup(self):
        resp = POKEMON.discord.get(DISCORD_POKEDAILY_SEARCH.format(discord_id=POKEMON.discord.data["user"]))
        latest_message = resp["messages"][0][0]
        message = Pokedaily.parse_message(latest_message["content"])

        timestamp = parse(latest_message["timestamp"])
        now = datetime.now()

        diff = now.timestamp() - timestamp.timestamp()

        message.add_last_redeemed(diff)

        last_redeemed = timedelta(
            hours=message.last_redeemed["hours"],
            minutes=message.last_redeemed["minutes"],
            seconds=message.last_redeemed["seconds"]
        )

        POKEMON.pokedaily_timer = datetime.utcnow() - last_redeemed
        self.log(f"{YELLOWLOG}Last Pokedaily at {POKEMON.pokedaily_timer}")

    def pokedaily_main(self):
        POKEMON.discord.post(DISCORD_POKEDAILY, "!pokedaily")

        if POKEMON.discord.data["user"] is None:
            POKEMON.discord.post(DISCORD_ALERTS, "Pokedaily, no user configured")
            self.log(f"{GREENLOG}Pokedaily, no user configured")
            return

        sleep(60 * 2)
        resp = POKEMON.discord.get(DISCORD_POKEDAILY_SEARCH.format(discord_id=POKEMON.discord.data["user"]))
        content = resp["messages"][0][0]["content"]
        message = Pokedaily.parse_message(content)

        if message.repeat:
            last_redeemed = timedelta(
                hours=message.last_redeemed["hours"],
                minutes=message.last_redeemed["minutes"],
                seconds=message.last_redeemed["seconds"]
            )

            self.log(f"{REDLOG}Pokedaily not ready")
            POKEMON.pokedaily_timer = datetime.utcnow() - last_redeemed

        else:
            POKEMON.reset_pokedaily_timer()
            POKEMON.discord.post(DISCORD_ALERTS, f"Pokedaily rewards ({message.rarity}):\n" + "\n".join(message.rewards))
            self.log(f"{GREENLOG}Pokedaily ({message.rarity}) rewards " + ", ".join(message.rewards))

    def wondertrade_main(self):
        self.get_missions()
        self.sort_computer()
        self.check_wondertrade()
        self.get_missions()

    def check_wondertrade(self):
        allpokemon = POKEMON.computer.pokemon
        if len(allpokemon) > 0:

            if POKEMON.wondertrade_timer is None:
                # get the timer from a pokemon
                pokemon = self.update_evolutions(allpokemon[0]["id"], allpokemon[0]["pokedexId"])

                can_trade_in = pokemon["tradable"]
                if can_trade_in is None:
                    POKEMON.wondertrade_timer = datetime.utcnow() - timedelta(hours=4)
                else:
                    if "hour" in can_trade_in:
                        hours = 2 - int(can_trade_in.split(" ")[0])
                    else:
                        hours = 2
                    if "minute" in can_trade_in:
                        minutes = 60 - int(can_trade_in.split(" ")[-2])
                    else:
                        minutes = 60

                    if minutes == 60:
                        minutes = 0
                        hours = hours + 1

                    POKEMON.wondertrade_timer = datetime.utcnow() - timedelta(minutes=minutes, hours=hours)

            if POKEMON.check_wondertrade():
                dex = self.pokemon_api.get_pokedex()
                POKEMON.sync_pokedex(dex)

                tradable = [pokemon for pokemon in allpokemon if pokemon["nickname"] is not None and "trade" in pokemon["nickname"]]
                pokemon_to_trade = []
                reasons = []
                best_nr_reasons = -1
                best_tier = ""
                trade_legendaries = POKEMON.wondertrade_legendaries
                trade_starters = POKEMON.wondertrade_starters

                for tier in ["S", "A", "B", "C"]:
                    looking_for = f"trade{tier}"
                    for pokemon in tradable:
                        if looking_for in pokemon["nickname"]:
                            if pokemon["locked"]:
                                continue

                            pokemon_object = self.get_pokemon_stats(pokemon["pokedexId"])
                            pokemon_object.level = pokemon["lvl"]

                            if pokemon_object.is_legendary and not trade_legendaries:
                                continue
                            if pokemon_object.is_starter and not trade_starters:
                                continue
                            if POKEMON.wondertrade_keep(pokemon_object):
                                continue

                            reasons = POKEMON.missions.check_all_wondertrade_missions(pokemon_object)
                            if len(reasons) < best_nr_reasons:
                                continue
                            elif len(reasons) > best_nr_reasons:
                                pokemon_to_trade = []
                                best_nr_reasons = len(reasons)
                                best_tier = tier
                            elif best_tier != tier:
                                continue
                            pokemon_to_trade.append(pokemon)

                if len(pokemon_to_trade) == 0:
                    self.log(f"{REDLOG}Could not find a pokemon to wondertrade")
                else:
                    sorted_pokemon_to_trade = sorted(pokemon_to_trade, key=lambda x: x["sellPrice"])

                    pokemon_traded = sorted_pokemon_to_trade[0]
                    pokemon_object = self.get_pokemon_stats(pokemon_traded["pokedexId"])
                    pokemon_object.level = pokemon_traded["lvl"]
                    reasons = POKEMON.missions.check_all_wondertrade_missions(pokemon_object)
                    pokemon_received = self.pokemon_api.wondertrade(pokemon_traded["id"])

                    if "pokemon" in pokemon_received:
                        pokemon_received = pokemon_received["pokemon"]
                        pokemon_traded_tier = self.get_pokemon_stats(pokemon_traded["pokedexId"]).tier
                        pokemon_received_tier = self.get_pokemon_stats(pokemon_received["pokedexId"]).tier

                        self.update_evolutions(pokemon_received["id"], pokemon_received["pokedexId"])

                        if POKEMON.pokedex.have(pokemon_received["name"]):
                            pokemon_received_need = ""
                            pokemon_sprite = None
                        else:
                            pokemon_received_need = " - needed"
                            sprite = str(pokemon_received["pokedexId"])
                            pokemon_sprite = get_sprite("pokemon", sprite, shiny=pokemon_received["isShiny"])

                        reasons_string = "" if len(reasons) == 0 else " ({})".format(", ".join(reasons))

                        wondertrade_msg = f"Wondertraded {pokemon_traded['name']} ({pokemon_traded_tier}){reasons_string} for {pokemon_received['name']} ({pokemon_received_tier}){pokemon_received_need}"
                        self.log(f"{GREENLOG}{wondertrade_msg}")
                        POKEMON.discord.post(DISCORD_ALERTS, wondertrade_msg, file=pokemon_sprite)
                        POKEMON.reset_wondertrade_timer()
                    else:
                        self.log(f"{REDLOG}Wondertrade {pokemon_traded['name']} failed {pokemon_received}")
                        POKEMON.wondertrade_timer = None
            else:
                time_remaining = POKEMON.check_wondertrade_left()
                time_str = str(time_remaining).split(".")[0]
                self.log(f"{YELLOWLOG}Wondertrade available in {time_str}")
        else:
            POKEMON.wondertrade_timer = None

    def update_evolutions(self, pokemon_id, pokedex_id):
        pokemon_data = self.pokemon_api.get_pokemon(pokemon_id)
        POKEMON.pokedex.set_evolutions(pokedex_id, pokemon_data["evolutionData"])
        POKEMON.pokedex.save_pokedex()
        return pokemon_data

    def check_bag_pokemon(self):
        for pokemon in POKEMON.computer.pokemon:
            pokemon_obj = self.get_pokemon_stats(pokemon["pokedexId"])
            updated = False

            if pokemon["name"] != pokemon_obj.name:
                POKEMON.pokedex.pokemon_stats[str(pokemon["pokedexId"])]["name"] = pokemon["name"]
                updated = True

            if pokemon["order"] != pokemon_obj.order:
                POKEMON.pokedex.pokemon_stats[str(pokemon["pokedexId"])]["order"] = pokemon["order"]
                updated = True

            if pokemon_obj.evolve_to is None:
                self.update_evolutions(pokemon["id"], pokemon["pokedexId"])
                self.log(f"{YELLOWLOG}Updated evolutions for{pokemon['pokedexId']}")
                sleep(1)
            elif updated:
                POKEMON.pokedex.save_pokedex()

    def daily_tasks(self, previous_date, current_date):
        self.stats_computer(previous_date, current_date)
        self.check_bag_pokemon()
        self.check_finish_pokedex()

    def check_finish_pokedex(self):
        must_catch = []
        can_evolve = []
        missing_pre_evo = []
        stones = {}
        required_pokemon = {}
        for i in range(1, POKEMON.pokedex.total + 1):
            pokemon = self.get_pokemon_stats(i)

            if pokemon.is_starter or pokemon.is_legendary or pokemon.is_non_spawnable or POKEMON.pokedex.have(pokemon):
                continue

            if len(pokemon.evolve_from) == 0:
                must_catch.append(pokemon.name)
                continue

            have_pre_to_evolve = False
            for pre_evolve in pokemon.evolve_from:
                pre_pokemon = self.get_pokemon_stats(pre_evolve)
                hits = POKEMON.computer.get_pokemon(pre_pokemon)
                if len(hits) > required_pokemon.get(pre_pokemon, 0):
                    required_pokemon[pre_pokemon] = required_pokemon.get(pre_pokemon, 0) + 1
                    have_pre_to_evolve = True
                    for evolve_into in pre_pokemon.evolve_to:
                        if evolve_into == str(pokemon.pokedex_id):
                            for stone in pre_pokemon.evolve_to[evolve_into]["stones"]:
                                stones[stone["stone"]] = stones.get(stone["stone"], 0) + stone["amount"]
                            break
                    break

            if have_pre_to_evolve:
                can_evolve.append(pokemon.name)
            else:
                missing_pre_evo.append(pokemon.name)

        discord_msg = "Pokedex Progress:"
        if len(must_catch) > 0:
            discord_msg += f"\n    Must Catch: {len(must_catch)} (" + ",".join(must_catch) + ")"
        if len(missing_pre_evo) > 0:
            discord_msg += f"\n    Missing Evo: {len(missing_pre_evo)} (" + ",".join(missing_pre_evo) + ")"
        if len(can_evolve) > 0:
            discord_msg += f"\n    Can Evolve: {len(can_evolve)} (" + ",".join(can_evolve) + ")"

        got_enough_stones = True
        if len(stones.keys()) > 0:
            discord_msg += "\n    Stone Requirements:"
            for stone in sorted(stones.keys()):
                stone_need = stones[stone]
                inv_stone = POKEMON.inventory.get_item(stone + " stone")
                stone_have = 0 if inv_stone is None else inv_stone["amount"]
                discord_msg += f"\n        {stone}: {stone_have}/{stone_need}"
                if stone_have >= stone_need:
                    discord_msg += " :white_check_mark:"
                else:
                    got_enough_stones = False

        if len(must_catch) == 0 and len(missing_pre_evo) == 0 and got_enough_stones:
            discord_msg += "\n\n    POKEDEX CAN BE COMPLETED!"

        POKEMON.discord.post(DISCORD_STATS, discord_msg)

    def stats_computer(self, previous_date, current_date):

        all_pokemon = self.pokemon_api.get_all_pokemon()
        POKEMON.sync_computer(all_pokemon)

        dex = self.pokemon_api.get_pokedex()
        POKEMON.sync_pokedex(dex)

        inv = self.pokemon_api.get_inventory()
        POKEMON.sync_inventory(inv)

        allpokemon = POKEMON.computer.pokemon

        spawnables_a = []
        spawnables_b = []
        spawnables_c = []

        for i in range(1, POKEMON.pokedex.total + 1):
            pokemon = self.get_pokemon_stats(i)

            if pokemon.is_starter or pokemon.is_legendary or pokemon.is_non_spawnable:
                continue

            if pokemon.tier == "A":
                spawnables_a.append(pokemon.name)
            elif pokemon.tier == "B":
                spawnables_b.append(pokemon.name)
            elif pokemon.tier == "C":
                spawnables_c.append(pokemon.name)

        spawnables_a_total = len(spawnables_a)
        spawnables_b_total = len(spawnables_b)
        spawnables_c_total = len(spawnables_c)

        spawnables_total = spawnables_a_total + spawnables_b_total + spawnables_c_total

        spawnables_a_have = len([pokemon for pokemon in spawnables_a if POKEMON.pokedex.have(pokemon)])
        spawnables_b_have = len([pokemon for pokemon in spawnables_b if POKEMON.pokedex.have(pokemon)])
        spawnables_c_have = len([pokemon for pokemon in spawnables_c if POKEMON.pokedex.have(pokemon)])
        spawnables_a_dont_have = [pokemon for pokemon in spawnables_a if POKEMON.pokedex.have(pokemon) is False]
        spawnables_b_dont_have = [pokemon for pokemon in spawnables_b if POKEMON.pokedex.have(pokemon) is False]
        spawnables_c_dont_have = [pokemon for pokemon in spawnables_c if POKEMON.pokedex.have(pokemon) is False]
        spawnables_have = spawnables_a_have + spawnables_b_have + spawnables_c_have

        spawnables_per = int(spawnables_have * 10000.0 / spawnables_total) / 100.0
        spawnables_a_per = int(spawnables_a_have * 10000.0 / spawnables_a_total) / 100.0
        spawnables_b_per = int(spawnables_b_have * 10000.0 / spawnables_b_total) / 100.0
        spawnables_c_per = int(spawnables_c_have * 10000.0 / spawnables_c_total) / 100.0

        results = {
            "shiny": [],
            "starter": [],
            "female": [],
            "legendary": [],
            "non_spawnable": [],
            "bag_regular": [],
            "bag_special": [],
        }

        for pokemon in allpokemon:
            if pokemon["isShiny"]:
                results["shiny"].append(pokemon)

            pokeobj = self.get_pokemon_stats(pokemon["pokedexId"])
            if pokeobj.is_starter:
                results["starter"].append(pokeobj.pokedex_id)
            if pokeobj.is_female:
                results["female"].append(pokeobj.pokedex_id)
            if pokeobj.is_legendary:
                results["legendary"].append(pokeobj.pokedex_id)
            if pokeobj.is_non_spawnable:
                results["non_spawnable"].append(pokeobj.pokedex_id)
            if pokeobj.pokedex_id <= POKEMON.pokedex.total:
                results["bag_regular"].append(pokeobj.pokedex_id)
            else:
                results["bag_special"].append(pokeobj.pokedex_id)

        results["shiny"] = len(results["shiny"])
        for k in ["starter", "female", "legendary", "bag_regular", "bag_special", "non_spawnable"]:
            results[k] = len(set(results[k]))

        for tier in ["S", "A", "B", "C"]:
            results[f"trade{tier}"] = len([pokemon for pokemon in allpokemon if pokemon["nickname"] is not None and f"trade{tier}" in pokemon["nickname"]])

        region_msg_list = []
        prefixes = POKEMON.pokedex.prefixes
        for region in prefixes:
            num = len(set([pokemon["pokedexId"] for pokemon in allpokemon if pokemon["name"].startswith(prefixes[region] + " ")]))
            if num > 0:
                region_msg_list.append((region, num, getattr(POKEMON.pokedex, region.lower())))

        region_msg = "".join([f"\n    {region}: {num}/{total}" for region, num, total in region_msg_list])

        tradable_total = sum([results[f"trade{tier}"] for tier in ["A", "B", "C"]])

        cash = POKEMON.inventory.cash
        pokeball = POKEMON.inventory.balls.get("pokeball", 0)
        premierball = POKEMON.inventory.balls.get("premierball", 0)
        greatball = POKEMON.inventory.balls.get("greatball", 0)
        ultraball = POKEMON.inventory.balls.get("ultraball", 0)
        otherball = sum([value for key, value in POKEMON.inventory.balls.items() if key not in ["pokeball", "premierball", "greatball", "ultraball"]])

        if POKEMON.inventory.have_item("battle coin"):
            coins = POKEMON.inventory.get_item("battle coin")["amount"]
        else:
            coins = 0

        max_show_missing = 20

        if len(spawnables_a_dont_have) == 0:
            missing_a_string = "Done"
        else:
            missing_a_string = "missing: " + ", ".join(spawnables_a_dont_have) if len(spawnables_a_dont_have) in range(0, max_show_missing) else ""

        if len(spawnables_b_dont_have) == 0:
            missing_b_string = "Done"
        else:
            missing_b_string = "missing: " + ", ".join(spawnables_b_dont_have) if len(spawnables_b_dont_have) in range(0, max_show_missing) else ""

        if len(spawnables_c_dont_have) == 0:
            missing_c_string = "Done"
        else:
            missing_c_string = "missing: " + ", ".join(spawnables_c_dont_have) if len(spawnables_c_dont_have) in range(0, max_show_missing) else ""

        battle_date = previous_date if previous_date is not None else current_date
        battle_stats = get_battle_logs(battle_date)

        discord_msg = f"""Bag Summary:

Starters: {results["starter"]}
Legendary: {results["legendary"]}
Non-Spawnables: {results["non_spawnable"]}/{POKEMON.pokedex.non_spawnables}
Shiny: {results["shiny"]}

Normal Version: {results["bag_regular"]}/{POKEMON.pokedex.total}
Alt Version: {results["bag_special"]}
    {CHARACTERS["female"]}: {results["female"]}/{POKEMON.pokedex.females}{region_msg}

Spawnables: {spawnables_have}/{spawnables_total} ({spawnables_per}%)
    A: {spawnables_a_have}/{spawnables_a_total} ({spawnables_a_per}%) {missing_a_string}
    B: {spawnables_b_have}/{spawnables_b_total} ({spawnables_b_per}%) {missing_b_string}
    C: {spawnables_c_have}/{spawnables_c_total} ({spawnables_c_per}%) {missing_c_string}

Tradables: {tradable_total}
    A: {results["tradeA"]}
    B: {results["tradeB"]}
    C: {results["tradeC"]}

Inventory: {cash}$ {coins} Battle Coins
    pokeball: {pokeball}
    premierball: {premierball}
    greatball: {greatball}
    ultraball: {ultraball}
    other: {otherball}

Battles:
    Wins: {battle_stats['wins']}/{battle_stats['battles']}
    Exp: {battle_stats['exp']}
    $: {battle_stats['cash']}
        """

        POKEMON.discord.post(DISCORD_STATS, discord_msg)

    def sort_computer(self):

        all_pokemon = self.pokemon_api.get_all_pokemon()
        POKEMON.sync_computer(all_pokemon)

        allpokemon = POKEMON.computer.pokemon
        pokedict = {}
        shineys = []
        changes = []

        for pokemon in allpokemon:
            if pokemon["isShiny"]:
                shineys.append(pokemon)
            else:
                pokedict.setdefault(pokemon["pokedexId"], []).append(pokemon)

        for pokeid in pokedict.keys():
            ordered = sorted(pokedict[pokeid], key=lambda x: (-x["avgIV"], -x["sellPrice"], -x["lvl"]))
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
                    if pokemon_obj.is_starter or pokemon_obj.is_legendary or pokemon_obj.is_female:
                        nick = pokemon["name"]
                        if pokemon_obj.is_starter:
                            nick = CHARACTERS["starter"] + nick
                        if pokemon_obj.is_legendary:
                            nick = CHARACTERS["legendary"] + nick
                        if pokemon_obj.is_female:
                            nick = nick + CHARACTERS["female"]
                    elif pokemon["nickname"] is None or pokemon["nickname"].startswith("trade") is False:
                        # if not starter and not female and has nickname, dont mess
                        continue
                    else:
                        nick = ""
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
                changes.append((pokemon["id"], nick, pokemon["name"], pokemon["nickname"]))

        for pokemon in shineys:
            if pokemon["nickname"] is not None:
                changes.append((pokemon["id"], "", pokemon["name"], pokemon["nickname"]))

        for poke_id, new_name, real_name, old_name in changes:
            if new_name is not None and len(new_name) > 12:
                self.log_file(f"{YELLOWLOG}Wont rename {real_name} from {old_name} to {new_name}, name too long")
                continue
            self.pokemon_api.set_name(poke_id, new_name)
            self.log_file(f"{YELLOWLOG}Renamed {real_name} from {old_name} to {new_name}")
            sleep(0.5)

    def check_inventory(self):
        inv = self.pokemon_api.get_inventory()
        POKEMON.sync_inventory(inv)

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
                        self.log(f"{GREENLOG}Purchased {buying} {ball['displayName']}s")

        if changes:
            inv = self.pokemon_api.get_inventory()
            POKEMON.sync_inventory(inv)

    def get_missions(self):
        missions = self.pokemon_api.get_missions()
        POKEMON.sync_missions(missions)

        completed = POKEMON.missions.get_completed()
        for title, reward in completed:
            readable_reward = reward["reward"]
            reward_sprite = get_sprite(reward["reward_type"], reward["reward_name"])
            mission_msg = f"Completed mission - {title} - reward: {readable_reward}"
            if reward["reward_type"] == "pokemon":
                if POKEMON.pokedex.have(reward["reward"]) is False:
                    mission_msg = mission_msg + " - needed"
                self.get_pokemon_stats(reward["reward_name"], cached=False)
            self.log(f"{GREENLOG}{mission_msg}")
            POKEMON.discord.post(DISCORD_ALERTS, mission_msg, file=reward_sprite)
            if reward_sprite is not None:
                reward_sprite.close()
        return completed

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

    def check_main(self, client):
        data = requests.get("https://poketwitch.bframework.de/info/events/last_spawn/").json()
        pokemon_id = data["pokedex_id"]

        pokemon = self.get_pokemon_stats(pokemon_id, cached=False)

        self.log_file(f"{YELLOWLOG}Pokemon spawned - processing {pokemon}")

        # sync everything
        dex = self.pokemon_api.get_pokedex()
        POKEMON.sync_pokedex(dex)

        all_pokemon = self.pokemon_api.get_all_pokemon()
        POKEMON.sync_computer(all_pokemon)

        self.check_inventory()

        self.get_missions()

        # find reasons to catch the pokemon
        catch_reasons, strategy = POKEMON.need_pokemon(pokemon)
        repeat = True

        for reason in ["pokedex", "bag", "alt"]:
            if reason in catch_reasons:
                repeat = False
                break

        if "ball" in catch_reasons:
            if strategy == "worst":
                for catch_ball in POKEMON.missions.data["ball"]:
                    if POKEMON.inventory.have_ball(catch_ball + "ball"):
                        ball = catch_ball + "ball"
                        strategy = "force"
                        break

        if len(catch_reasons) > 0:
            if strategy != "force":
                ball = POKEMON.inventory.get_catch_ball(pokemon, repeat=repeat, strategy=strategy)

            if ball is None:
                self.log_file(f"{REDLOG}Won't catch {pokemon.name} ran out of balls (strategy: {strategy})")
            else:
                twitch_channel = POKEMON.get_channel()
                message = f"!pokecatch {ball}"
                client.privmsg("#" + twitch_channel, message)

                reasons_string = ", ".join(catch_reasons)
                self.log_file(f"{GREENLOG}Trying to catch {pokemon.name} with {ball} because {reasons_string}")

                sleep(5)

                all_pokemon = self.pokemon_api.get_all_pokemon()
                POKEMON.sync_computer(all_pokemon)

                # find all the pokemon that are the current one that spawned
                filtered = POKEMON.computer.get_pokemon(pokemon)
                caught = None
                for poke in filtered:
                    if (datetime.utcnow() - parse(poke["caughtAt"][:-1])).total_seconds() < 60 * 5:
                        caught = poke
                        break

                self.log(f"{GREENLOG}Trying to catch in {twitch_channel}")
                if caught is not None:
                    ivs = int(poke["avgIV"])
                    lvl = poke['lvl']
                    shiny = " Shiny" if poke["isShiny"] else ""
                    self.log_file(f"{GREENLOG}Caught{shiny} {pokemon.name} ({pokemon.tier}) Lvl.{lvl} {ivs}IV")
                    msg = f"I caught a{shiny} {pokemon.name} ({pokemon.tier}) Lvl.{lvl} {ivs}IV!"
                    if pokemon.is_fish and FISH_EVENT:
                        caught_pokemon = self.update_evolutions(poke["id"], pokemon_id)
                        if "🐟" in caught_pokemon["description"]:
                            msg += "\n" + caught_pokemon["description"].split("Your fish is ")[-1].split("Your fish has ")[-1]

                    sprite = str(poke["pokedexId"])
                    pokemon_sprite = get_sprite("pokemon", sprite, shiny=poke["isShiny"])
                else:
                    self.log_file(f"{REDLOG}Failed to catch {pokemon.name} ({pokemon.tier})")
                    msg = f"I missed {pokemon.name} ({pokemon.tier})!"
                    pokemon_sprite = None

                msg = msg + f" {ball}, because {reasons_string}"

                POKEMON.discord.post(DISCORD_ALERTS, msg, file=pokemon_sprite)

                # check for hidden chat rewards (stones, candys & golden tickets)
                completed_missions = self.get_missions()
                item_rewards = [reward for (_, reward) in completed_missions if reward["reward_type"] != "pokemon"]
                mission_items = {reward["item_name"].lower(): reward["item_amount"] for reward in item_rewards}

                old_items = copy.deepcopy(POKEMON.inventory.items)
                inv = self.pokemon_api.get_inventory()
                POKEMON.sync_inventory(inv)

                for item_name in POKEMON.inventory.items:
                    item = POKEMON.inventory.get_item(item_name)
                    old_item = old_items.get(item_name, {"amount": 0})
                    if item["category"] != "evolution" and item_name not in ["rare candy", "golden ticket"]:
                        continue

                    amount_got = item["amount"] - old_item["amount"] - mission_items.get(item_name, 0)
                    if amount_got < 1:
                        continue

                    item_str = item["name"]
                    if amount_got == 1:
                        prefix = "an" if item_name[0] in ["a", "e", "i", "o", "u"] else "a"
                    else:
                        prefix = amount_got

                    rewards_msg = f"You got {prefix} {item_str} from your last catch!"
                    sprite = get_sprite(item["category"], item["sprite"])
                    POKEMON.discord.post(DISCORD_ALERTS, rewards_msg, file=sprite)

                if caught is not None:
                    # check for loyalty tier up
                    rewards = POKEMON.increment_loyalty(twitch_channel)
                    if rewards is not None:
                        reward, next_reward = rewards
                        rewards_msg = f"Loyalty tier completed in {twitch_channel}, new reward: {reward}"
                        self.log(f"{GREENLOG}{rewards_msg}")
                        if next_reward is not None:
                            rewards_msg = rewards_msg + f"\nNext reward: {next_reward}"
                            self.log(f"{GREENLOG}next reward: {next_reward}")
                        sprite = get_sprite("streamer", twitch_channel)
                        POKEMON.discord.post(DISCORD_ALERTS, rewards_msg, file=sprite)
        else:
            self.log_file(f"{REDLOG}Don't need pokemon, skipping")

            twitch_channel = POKEMON.get_channel(ignore_priority=False)
            client.privmsg("#" + twitch_channel, "!pokecheck")
            self.log(f"{GREENLOG}Pokecheck in {twitch_channel}")

            self.get_missions()


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
        logger.info(
            f"Join IRC Chat: {self.channel}", extra={"emoji": ":speech_balloon:"}
        )
        POKEMON.channel_online(self.channel)
        self.chat_irc.start()

    def stop(self):
        ThreadChatO.stop(self)
        leave_channel(self.channel)


def leave_channel(channel):
    if channel in POKEMON.channel_list:
        POKEMON.remove_channel(channel)
        logger.info(
            f"Leaving Pokemon: {channel}", extra={"emoji": ":speech_balloon:"}
        )
        if len(POKEMON.channel_list) == 0:
            poke_logger.info("Nobody is streaming Pokemon CG")

    if channel in POKEMON.online_channels:
        POKEMON.channel_offline(channel)

    THREADCONTROLLER.remove_client(channel)


ChatPresence = ChatPresenceO
