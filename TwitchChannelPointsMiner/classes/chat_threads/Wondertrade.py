from time import sleep
import traceback

from ..entities.Pokemon import get_sprite

from ..ChatUtils import (
    CHARACTERS,
    DISCORD_ALERTS,
    log,
    log_file,
    POKEMON,
    seconds_readable,
    WONDERTRADE_DELAY,
)


class Wondertrade(object):
    def wondertrade_timer(self):
        thread_name = "Wondertrade Timer"
        max_wait = 60 * 60  # 1 hour
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
                remaining_time -= wait

            try:
                self.wondertrade()
                remaining_time = WONDERTRADE_DELAY
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
        POKEMON.sync_computer(all_pokemon)

        allpokemon = POKEMON.computer.pokemon
        # get the timer from a pokemon
        pokemon = self.update_evolutions(allpokemon[0]["id"], allpokemon[0]["pokedexId"])

        can_trade_in = pokemon["tradable"]
        if can_trade_in is None:
            return 1
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
        self.do_wondertrade()
        self.get_missions()

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
                changes.append((pokemon["id"], nick, pokemon["name"], pokemon["nickname"]))

        for pokemon in shineys:
            if pokemon["nickname"] is not None:
                changes.append((pokemon["id"], "", pokemon["name"], pokemon["nickname"]))

        for poke_id, new_name, real_name, old_name in changes:
            if new_name is not None and len(new_name) > 12:
                log_file("yellow", f"Wont rename {real_name} from {old_name} to {new_name}, name too long")
                continue
            self.pokemon_api.set_name(poke_id, new_name)
            log_file("yellow", f"Renamed {real_name} from {old_name} to {new_name}")
            sleep(0.5)

    def do_wondertrade(self):
        allpokemon = POKEMON.computer.pokemon
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
            log("red", f"Could not find a pokemon to wondertrade")
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
                pokemon_received_obj = self.get_pokemon_stats(pokemon_received["pokedexId"])
                pokemon_received_tier = pokemon_received_obj.tier

                self.update_evolutions(pokemon_received["id"], pokemon_received["pokedexId"])

                if POKEMON.pokedex.have(pokemon_received_obj):
                    pokemon_received_need = ""
                    pokemon_sprite = None
                else:
                    pokemon_received_need = " - needed"
                    sprite = str(pokemon_received["pokedexId"])
                    pokemon_sprite = get_sprite("pokemon", sprite, shiny=pokemon_received["isShiny"])

                reasons_string = "" if len(reasons) == 0 else " ({})".format(", ".join(reasons))

                wondertrade_msg = f"Wondertraded {pokemon_traded['name']} ({pokemon_traded_tier}){reasons_string} for {pokemon_received['name']} ({pokemon_received_tier}){pokemon_received_need}"
                log("green", f"{wondertrade_msg}")
                POKEMON.discord.post(DISCORD_ALERTS, wondertrade_msg, file=pokemon_sprite)
            else:
                log("red", f"Wondertrade {pokemon_traded['name']} failed {pokemon_received}")