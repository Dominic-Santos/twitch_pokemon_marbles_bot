from time import sleep
import requests
import traceback
from datetime import datetime
from dateutil.parser import parse
import copy


from ..ChatUtils import (
    DISCORD_ALERTS,
    FISH_EVENT,
    log,
    log_file,
    POKEMON,
    seconds_readable,
    THREADCONTROLLER,
)
from ..entities.Pokemon import get_sprite


def get_next_spawn():
    data = requests.get("https://poketwitch.bframework.de/info/events/last_spawn/").json()
    return data["next_spawn"] + 2


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
        data = requests.get("https://poketwitch.bframework.de/info/events/last_spawn/").json()
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
                log_file("red", f"Won't catch {pokemon.name} ran out of balls (strategy: {strategy})")
            else:
                twitch_channel = POKEMON.get_channel()

                reasons_string = ", ".join(catch_reasons)
                log_file("green", f"Trying to catch {pokemon.name} with {ball} because {reasons_string}")

                message = f"!pokecatch {ball}"
                client.privmsg("#" + twitch_channel, message)

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

                log("green", f"Trying to catch in {twitch_channel}")
                if caught is not None:
                    ivs = int(poke["avgIV"])
                    lvl = poke['lvl']
                    shiny = " Shiny" if poke["isShiny"] else ""
                    log_file("green", f"Caught{shiny} {pokemon.name} ({pokemon.tier}) Lvl.{lvl} {ivs}IV")
                    msg = f"I caught a{shiny} {pokemon.name} ({pokemon.tier}) Lvl.{lvl} {ivs}IV!"
                    if pokemon.is_fish and FISH_EVENT:
                        caught_pokemon = self.update_evolutions(poke["id"], pokemon_id)
                        if "🐟" in caught_pokemon["description"]:
                            msg += "\n" + caught_pokemon["description"].split("Your fish is ")[-1].split("Your fish has ")[-1]

                    sprite = str(poke["pokedexId"])
                    pokemon_sprite = get_sprite("pokemon", sprite, shiny=poke["isShiny"])
                else:
                    log_file("red", f"Failed to catch {pokemon.name} ({pokemon.tier})")
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
                        log("green", f"{rewards_msg}")
                        if next_reward is not None:
                            rewards_msg = rewards_msg + f"\nNext reward: {next_reward}"
                            log("green", f"next reward: {next_reward}")
                        sprite = get_sprite("streamer", twitch_channel)
                        POKEMON.discord.post(DISCORD_ALERTS, rewards_msg, file=sprite)
        else:
            log_file("green", f"Don't need pokemon, Pokecheck in {twitch_channel}")
            twitch_channel = POKEMON.get_channel(ignore_priority=False)
            client.privmsg("#" + twitch_channel, "!pokecheck")
            self.get_missions()
