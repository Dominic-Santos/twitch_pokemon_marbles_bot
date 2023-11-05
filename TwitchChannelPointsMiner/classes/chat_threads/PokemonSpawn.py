from time import sleep
import requests
import traceback

from .DailyTasks import discord_update_pokedex

from ..entities.Pokemon import get_sprite

from ..ChatLogs import log, log_file
from ..ChatUtils import (
    DISCORD_ALERTS,
    POKEMON,
    seconds_readable,
    THREADCONTROLLER,
)


def get_spawn():
    return requests.get("https://poketwitch.bframework.de/info/events/last_spawn/").json()


def get_next_spawn():
    data = get_spawn()
    return data["next_spawn"] + 2


def get_current_spawn():
    data = get_spawn()
    return 15 * 60 - data["next_spawn"]


class PokemonSpawn(object):
    def spawn_timer(self):
        thread_name = "Spawn Timer"
        log("yellow", f"Thread Created - {thread_name}")

        running = True
        exit = False
        remaining_time = 0

        while running and exit is False:
            try:
                remaining_time = get_next_spawn()
                running = False
            except KeyboardInterrupt:
                exit = True
            except Exception as ex:
                str_ex = str(ex)
                log("red", f"{thread_name} Error - {str_ex}")
                print(traceback.format_exc())
                sleep(5)

        while exit is False:
            remaining_human = seconds_readable(remaining_time)
            log("yellow", f"{thread_name} - Waiting for {remaining_human}")
            sleep(remaining_time)

            client_channel, client = THREADCONTROLLER.get_client()
            try:
                if client is not None:
                    self.spawn(client)
                remaining_time = get_next_spawn()
            except KeyboardInterrupt:
                exit = True
            except Exception as ex:
                remaining_time = 5
                str_ex = str(ex)
                log("red", f"{thread_name} Error - {str_ex}")
                THREADCONTROLLER.remove_client(client_channel)
                print(traceback.format_exc())

        log("yellow", f"Thread Closing - {thread_name}")

    def spawn(self, client):
        data = get_spawn()
        pokemon_id = data["pokedex_id"]

        pokemon = self.get_pokemon_stats(pokemon_id, cached=False)

        log_file("yellow", f"Pokemon spawned - processing {pokemon}")

        # sync everything
        dex = self.pokemon_api.get_pokedex()
        POKEMON.sync_pokedex(dex)

        all_pokemon = self.pokemon_api.get_all_pokemon()
        POKEMON.sync_computer(all_pokemon)

        self.check_inventory()

        self.get_missions()

        # find reasons to catch the pokemon
        catch_reasons = POKEMON.need_pokemon(pokemon)

        if len(catch_reasons) == 0:
            twitch_channel = POKEMON.get_channel(ignore_priority=False)
            log_file("yellow", f"Don't need pokemon, Pokecheck in {twitch_channel}")

            client.privmsg("#" + twitch_channel, "!pokecheck")
            self.get_missions()
            return

        mission_balls = [] if "ball" not in catch_reasons else POKEMON.missions.data["ball"]
        ball = POKEMON.inventory.get_catch_ball(pokemon, catch_reasons, mission_balls)

        if ball is None:
            log_file("red", f"Won't catch {pokemon.name}, ran out of balls")
            return

        twitch_channel = POKEMON.get_channel()

        reasons_string = ", ".join(catch_reasons)
        message = f"!pokecatch {ball}"

        if ball == "timerball":
            wait = 85 - get_current_spawn()
            log("green", f"Timerball selected, waiting {wait} seconds to catch")
            sleep(wait)

        log_file("green", f"Trying to catch {pokemon.name} with {ball} because {reasons_string}")
        log("green", f"Trying to catch in {twitch_channel}")

        client.privmsg("#" + twitch_channel, message)

        sleep(5)

        pokemon, caught = self.get_last_caught(pokemon_id)

        pokemon_sprite = None
        if caught is not None:
            ivs = int(caught["avgIV"])
            lvl = caught['lvl']
            shiny = " Shiny" if caught["isShiny"] else ""
            unidentified = " (Unidentified Ghost)" if pokemon.is_unidentified_ghost else ""
            msg = f"Caught{unidentified}{shiny} {pokemon.name} ({pokemon.tier}) Lvl.{lvl} {ivs}IV"
            log_file("green", msg)

            caught_pokemon = self.update_evolutions(caught["id"], pokemon.pokedex_id)

            if pokemon.is_fish and POKEMON.fish_event:
                if "🐟" in caught_pokemon["description"]:
                    msg += "\n" + caught_pokemon["description"].split("Your fish is ")[-1].split("Your fish has ")[-1]

            sprite = str(caught["pokedexId"])
            extra_reasons = {"shiny": caught["isShiny"]}
            if POKEMON.show_sprite(catch_reasons, extra_reasons):
                pokemon_sprite = get_sprite("pokemon", sprite, shiny=caught["isShiny"])

            if "pokedex" in catch_reasons and pokemon.is_spawnable:
                discord_update_pokedex(POKEMON, self.pokemon_api, self.get_pokemon_stats)

        else:
            log_file("red", f"Failed to catch {pokemon.name} ({pokemon.tier})")
            msg = f"Missed {pokemon.name} ({pokemon.tier})!"

        msg = msg + f" {ball}, because {reasons_string}"

        POKEMON.discord.post(DISCORD_ALERTS, msg, file=pokemon_sprite)

        self.update_inventory()

        if caught is not None:
            # check for loyalty tier up
            rewards = POKEMON.increment_loyalty(twitch_channel)
            if rewards is not None:
                reward, next_reward = rewards
                rewards_msg = f"Loyalty tier completed in {twitch_channel}, new reward: {reward}"
                log("green", f"{rewards_msg}")
                if next_reward is not None:
                    rewards_msg = rewards_msg + f"\nNext reward: {next_reward}"
                    log("green", f"next reward: {next_reward}")
                sprite = get_sprite("streamer", twitch_channel)
                POKEMON.discord.post(DISCORD_ALERTS, rewards_msg, file=sprite)
