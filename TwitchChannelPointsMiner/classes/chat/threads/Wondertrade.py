from time import sleep
import traceback

from ...entities.Pokemon import get_sprite
from ...utils import check_pokedex

from ..ChatLogs import log
from ...Utils import (
    DISCORD_ALERTS,
    seconds_readable,
)


class Wondertrade(object):
    def wondertrade_timer(self):
        thread_name = "Wondertrade Timer"
        max_wait = 60 * 30  # 30 mins
        log("yellow", f"Thread Created - {thread_name}")

        running = True
        exit = False
        remaining_time = 0

        while running and exit is False:
            try:
                remaining_time = self.get_next_wondertrade()
                running = False
            except KeyboardInterrupt:
                exit = True
            except Exception as ex:
                str_ex = str(ex)
                log("red", f"{thread_name} Error - {str_ex}")
                print(traceback.format_exc())
                sleep(5)

        while exit is False:
            while remaining_time > 0:
                remaining_human = seconds_readable(remaining_time)
                log("yellow", f"{thread_name} - Waiting for {remaining_human}")
                wait = min(max_wait, remaining_time)
                sleep(wait)
                remaining_time = self.get_next_wondertrade()

            try:
                sleep(1)
                self.wondertrade()
                sleep(5)
                remaining_time = self.get_next_wondertrade()
            except KeyboardInterrupt:
                exit = True
            except Exception as ex:
                remaining_time = 5
                str_ex = str(ex)
                log("red", f"{thread_name} Error - {str_ex}")
                print(traceback.format_exc())

        log("yellow", f"Thread Closing - {thread_name}")

    def get_next_wondertrade(self):
        all_pokemon = self.pokemon_api.get_all_pokemon()
        self.pokemon.sync_computer(all_pokemon)

        allpokemon = self.pokemon.computer.pokemon
        # get the timer from a pokemon
        pokemon = self.update_evolutions(allpokemon[0]["id"], allpokemon[0]["pokedexId"])

        can_trade_in = pokemon["tradable"]
        if can_trade_in is None:
            return 0
        else:
            if "hour" in can_trade_in:
                hours = int(can_trade_in.split(" ")[0])
            else:
                hours = 0

            if "minute" in can_trade_in:
                minutes = int(can_trade_in.split(" ")[-2])
            else:
                minutes = 0

            return 60 + minutes * 60 + hours * 60 * 60

    def wondertrade(self):
        log("yellow", f"Running Wondertrade")
        self.get_missions()
        self.sort_computer()
        received = self.do_wondertrade()
        self.get_missions()

        if received is not None:
            self.sync_pokemon_data(pokemon_id=received["id"])

    def do_wondertrade(self):
        allpokemon = self.pokemon.computer.pokemon
        dex = self.pokemon_api.get_pokedex()
        self.pokemon.sync_pokedex(dex)

        tradable = [pokemon for pokemon in allpokemon if pokemon["nickname"] is not None and "trade" in pokemon["nickname"]]
        pokemon_to_trade = []
        reasons = []
        best_nr_reasons = -1
        best_tier = ""
        trade_legendaries = self.pokemon.wondertrade_legendaries
        trade_starters = self.pokemon.wondertrade_starters

        for tier in self.pokemon.wondertrade_tiers:
            looking_for = f"trade{tier}"
            for pokemon in tradable:
                if looking_for in pokemon["nickname"]:
                    if pokemon["locked"]:
                        continue

                    if pokemon["lvl"] > self.pokemon.settings["trade_level_max"]:
                        continue

                    pokemon_object = self.get_pokemon_stats(pokemon["pokedexId"])
                    if pokemon_object.is_egg:
                        continue

                    pokemon_object.level = pokemon["lvl"]

                    if pokemon_object.is_legendary and not trade_legendaries:
                        continue
                    if pokemon_object.is_starter and not trade_starters:
                        continue
                    if self.pokemon.wondertrade_keep(pokemon_object):
                        continue

                    reasons = self.pokemon.missions.check_all_wondertrade_missions(pokemon_object)
                    if self.pokemon.settings["hatch_eggs"] and self.pokemon.poke_buddy is not None:
                        buddy = self.get_pokemon_stats(self.pokemon.poke_buddy["pokedexId"])
                        for reason in self.pokemon.egg_trade_reasons(pokemon_object, buddy):
                            if reason not in reasons:
                                reasons.append(reason)

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
            log("red", f"Could not find a pokemon to wondertrade")
        else:
            sorted_pokemon_to_trade = sorted(pokemon_to_trade, key=lambda x: x["sellPrice"])

            pokemon_traded = sorted_pokemon_to_trade[0]
            pokemon_object = self.get_pokemon_stats(pokemon_traded["pokedexId"])
            pokemon_object.level = pokemon_traded["lvl"]
            reasons = self.pokemon.missions.check_all_wondertrade_missions(pokemon_object)
            if self.pokemon.settings["hatch_eggs"] and self.pokemon.poke_buddy is not None:
                buddy = self.get_pokemon_stats(self.pokemon.poke_buddy["pokedexId"])
                for reason in self.pokemon.egg_trade_reasons(pokemon_object, buddy):
                    if reason not in reasons:
                        reasons.append(reason)
            pokemon_received = self.pokemon_api.wondertrade(pokemon_traded["id"])

            if "pokemon" in pokemon_received:
                pokemon_received = pokemon_received["pokemon"]
                pokemon_traded_tier = self.get_pokemon_stats(pokemon_traded["pokedexId"]).tier
                pokemon_received_obj = self.get_pokemon_stats(pokemon_received["pokedexId"])
                pokemon_received_tier = pokemon_received_obj.tier

                self.update_evolutions(pokemon_received["id"], pokemon_received["pokedexId"])

                if self.pokemon.pokedex.have(pokemon_received_obj):
                    pokemon_received_need = ""
                    pokemon_sprite = None
                else:
                    pokemon_received_need = " - needed"
                    sprite = str(pokemon_received["pokedexId"])
                    pokemon_sprite = get_sprite("pokemon", sprite, shiny=pokemon_received["isShiny"])
                    if pokemon_received_obj.is_spawnable:
                        check_pokedex(self.pokemon, self.pokemon_api, self.get_pokemon_stats)

                reasons_string = "" if len(reasons) == 0 else " ({})".format(", ".join(reasons))

                wondertrade_msg = f"Wondertraded {pokemon_traded['name']} ({pokemon_traded_tier}){reasons_string} for {pokemon_received['name']} ({pokemon_received_tier}){pokemon_received_need}"
                log("green", f"{wondertrade_msg}")
                self.pokemon.discord.post(DISCORD_ALERTS, wondertrade_msg, file=pokemon_sprite)

                self.sort_computer([pokemon_received["pokedexId"]])
                return pokemon_received
            else:
                log("red", f"Wondertrade {pokemon_traded['name']} failed {pokemon_received}")
