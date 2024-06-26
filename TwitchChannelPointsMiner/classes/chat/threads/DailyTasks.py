from datetime import datetime
from time import sleep
import traceback

from ..ChatLogs import log
from ...Utils import DISCORD_STATS
from ...utils import (
    check_pokedex,
    get_catch_rates,
    money_graph, MONEY_GRAPH_IMAGE,
    catch_graph, CATCH_GRAPH_IMAGE,
    battle_summary,
    stats_computer,
    check_finish_pokedex,
)


class DailyTasks(object):

    def daily_task_timer(self):
        thread_name = "Daily Task"
        log("yellow", f"Thread Created - {thread_name}")
        running = True
        previous = None

        while running:
            try:
                cur_date = datetime.now().date()
                if cur_date != previous:
                    self.daily_tasks(previous, cur_date)
                    previous = cur_date
            except KeyboardInterrupt:
                running = False
            except Exception as ex:
                str_ex = str(ex)
                log("red", f"{thread_name} Error - {str_ex}")
                print(traceback.format_exc())
            sleep(15 * 60)  # 15 mins

        log("yellow", f"Thread Closing - {thread_name}")

    def daily_tasks(self, previous_date, current_date):
        log("yellow", f"Running Daily Tasks")
        stats_date = previous_date if previous_date is not None else current_date
        self.stats_computer()
        self.battle_summary(stats_date)
        self.check_bag_pokemon()
        self.check_finish_pokedex()
        self.catch_rates(stats_date)
        self.check_loyalty()
        if self.pokemon.settings["daily_money_graph"]:
            self.money_graph()
        if self.pokemon.settings["daily_catch_graph"]:
            self.catch_graph()
        self.clean_pokemon_computer_stats()

    def clean_pokemon_computer_stats(self):
        try:
            cleaned = self.pokemon.computer.clean_data()
            self.pokemon.computer.save_computer()
            log("yellow", f"Computer Stats Cleaned - removed {cleaned} old values")
        except Exception as e:
            log("red", "Computer Stats Cleaned - failed " + str(e))

    def catch_graph(self):
        catch_graph(self.pokemon.discord, mode="tiers")
        self.pokemon.discord.post(DISCORD_STATS, "Catch Graph Tiers", file=open(CATCH_GRAPH_IMAGE, "rb"))

        catch_graph(self.pokemon.discord, mode="total")
        self.pokemon.discord.post(DISCORD_STATS, "Catch Graph Total", file=open(CATCH_GRAPH_IMAGE, "rb"))

    def money_graph(self):
        money_graph(self.pokemon.discord)
        self.pokemon.discord.post(DISCORD_STATS, "Money Graph", file=open(MONEY_GRAPH_IMAGE, "rb"))

    def stats_computer(self):
        all_pokemon = self.pokemon_api.get_all_pokemon()
        self.pokemon.sync_computer(all_pokemon)

        self.update_inventory()

        discord_msg = stats_computer(self.pokemon, self.get_pokemon_stats)

        self.pokemon.discord.post(DISCORD_STATS, discord_msg)

        self.show_pokedex()

    def show_pokedex(self):
        check_pokedex(self.pokemon, self.pokemon_api, self.get_pokemon_stats)

    def battle_summary(self, battle_date):
        discord_msg = battle_summary(battle_date)

        self.pokemon.discord.post(DISCORD_STATS, discord_msg)

    def check_bag_pokemon(self):
        for pokemon in self.pokemon.computer.pokemon:
            pokemon_obj = self.get_pokemon_stats(pokemon["pokedexId"])
            updated = False

            if pokemon["name"] != pokemon_obj.name:
                self.pokemon.pokedex.pokemon_stats[str(pokemon["pokedexId"])]["name"] = pokemon["name"]
                updated = True

            if pokemon["order"] != pokemon_obj.order:
                self.pokemon.pokedex.pokemon_stats[str(pokemon["pokedexId"])]["order"] = pokemon["order"]
                updated = True

            if pokemon_obj.evolve_to is None:
                self.update_evolutions(pokemon["id"], pokemon["pokedexId"])
                log("yellow", f"Updated evolutions for {pokemon['pokedexId']}")
                sleep(1)
            elif updated:
                self.pokemon.pokedex.save_pokedex()

    def check_finish_pokedex(self):
        discord_msg = check_finish_pokedex(self.pokemon, self.get_pokemon_stats)

        self.pokemon.discord.post(DISCORD_STATS, discord_msg)

    def catch_rates(self, the_date):
        discord_msg = get_catch_rates(the_date)

        self.pokemon.discord.post(DISCORD_STATS, discord_msg)

    def check_loyalty(self):
        discord_msg = self.pokemon.get_loyalty_readable(with_featured=False, with_zeros=False)

        self.pokemon.discord.post(DISCORD_STATS, discord_msg)
