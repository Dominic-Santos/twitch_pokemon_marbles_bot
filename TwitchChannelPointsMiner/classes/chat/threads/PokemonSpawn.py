from time import sleep
from datetime import datetime
import requests
import traceback

from ...entities.Pokemon import get_sprite
from ...utils import check_pokedex

from ..ChatLogs import log, log_file
from ...Utils import (
    DISCORD_ALERTS,
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
                    self.check_pokebuddy()
                    self.spawn(client)
                    self.check_pokebuddy(cached=True)
                    self.sync_pokemon_data()
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

        spawned_pokemon = self.get_pokemon_stats(pokemon_id, cached=False)

        log_file("yellow", f"Pokemon spawned - processing {spawned_pokemon}")

        # sync everything
        dex = self.pokemon_api.get_pokedex()
        self.pokemon.sync_pokedex(dex)

        all_pokemon = self.pokemon_api.get_all_pokemon()
        self.pokemon.sync_computer(all_pokemon)

        self.check_inventory()

        self.get_missions()

        # find reasons to catch the pokemon
        catch_reasons = self.pokemon.need_pokemon(spawned_pokemon)
        catch_balls = [] if "ball" not in catch_reasons else self.pokemon.missions.data["ball"]

        if self.pokemon.poke_buddy is not None and self.pokemon.settings["hatch_eggs"]:
            buddy_obj = self.get_pokemon_stats(self.pokemon.poke_buddy["pokedexId"])
            egg_reason, egg_ball = self.pokemon.egg_catch_reasons(spawned_pokemon, buddy_obj)

            if egg_reason is not None:
                if egg_reason not in catch_reasons:
                    catch_reasons.append(egg_reason)

            if egg_ball is not None:
                if egg_ball not in catch_balls:
                    catch_balls.append(egg_ball)

        if len(catch_reasons) == 0:
            twitch_channel = self.pokemon.get_channel(ignore_priority=False)
            now = datetime.now()

            if now.hour > 7:
                log_file("yellow", f"Don't need pokemon, Pokecheck in {twitch_channel}")
                client.privmsg("#" + twitch_channel, "!pokecheck")
            else:
                log_file("yellow", f"Don't need pokemon, won't pokecheck")
            self.get_missions()
            return

        ball = self.pokemon.inventory.get_catch_ball(spawned_pokemon, catch_reasons, catch_balls)

        if ball is None:
            log_file("red", f"Won't catch {spawned_pokemon.name}, ran out of balls")
            return

        twitch_channel = self.pokemon.get_channel()

        reasons_string = ", ".join(catch_reasons)
        message = f"!pokecatch {ball}"

        if ball == "timerball":
            wait = 85 - get_current_spawn()
            log("green", f"Timerball selected, waiting {wait} seconds to catch")
            sleep(wait)

        log_file("green", f"Trying to catch {spawned_pokemon.name} with {ball} because {reasons_string}")
        log("green", f"Trying to catch in {twitch_channel}")

        client.privmsg("#" + twitch_channel, message)

        for i in range(3):
            sleep(5)
            log("yellow", f"Checking if caught pokemon")
            pokemon, caught = self.get_last_caught(pokemon_id)
            if caught is not None:
                break

        pokemon_sprite = None
        if caught is not None:
            ivs = int(caught["avgIV"])
            lvl = caught['lvl']
            shiny = " Shiny" if caught["isShiny"] else ""
            unidentified = f" ({spawned_pokemon.name})" if pokemon.is_unidentified_spawn else ""
            msg = f"Caught{unidentified}{shiny} {pokemon.name} ({pokemon.tier}) Lvl.{lvl} {ivs}IV"
            log_file("green", msg)

            caught_pokemon = self.update_evolutions(caught["id"], pokemon.pokedex_id)

            if pokemon.is_fish and self.pokemon.fish_event:
                if "🐟" in caught_pokemon["description"]:
                    msg += "\n" + caught_pokemon["description"].split("Your fish is ")[-1].split("Your fish has ")[-1]

            sprite = str(caught["pokedexId"])
            extra_reasons = {"shiny": caught["isShiny"]}
            if self.pokemon.show_sprite(catch_reasons, extra_reasons):
                pokemon_sprite = get_sprite("pokemon", sprite, shiny=caught["isShiny"])

            if "pokedex" in catch_reasons and pokemon.is_spawnable:
                check_pokedex(self.pokemon, self.pokemon_api, self.get_pokemon_stats)

            egg_data, egg_bag = self.check_got_dragon_egg()
            if egg_bag is not None:
                egg_name = egg_bag["name"]
                egg_sprite = get_sprite("pokemon", str(egg_bag["pokedexId"]), shiny=False)
                self.pokemon.discord.post(DISCORD_ALERTS, f"🥚You got a {egg_name}🥚", file=egg_sprite)
                self.update_evolutions(egg_bag["id"], egg_data.pokedex_id)

        else:
            log_file("red", f"Failed to catch {spawned_pokemon.name} ({spawned_pokemon.tier})")
            msg = f"Missed {spawned_pokemon.name} ({spawned_pokemon.tier})!"

        msg = msg + f" {ball}, because {reasons_string}"

        self.pokemon.discord.post(DISCORD_ALERTS, msg, file=pokemon_sprite)

        self.update_inventory()

        self.sort_computer([pokemon_id])

        if caught is not None:
            # check for loyalty tier up
            rewards = self.pokemon.increment_loyalty(twitch_channel)
            if rewards is not None:
                reward, next_reward = rewards
                rewards_msg = f"Loyalty tier completed in {twitch_channel}, new reward: {reward}"
                log("green", f"{rewards_msg}")
                if next_reward is not None:
                    rewards_msg = rewards_msg + f"\nNext reward: {next_reward}"
                    log("green", f"next reward: {next_reward}")
                sprite = get_sprite("streamer", twitch_channel)
                self.pokemon.discord.post(DISCORD_ALERTS, rewards_msg, file=sprite)
