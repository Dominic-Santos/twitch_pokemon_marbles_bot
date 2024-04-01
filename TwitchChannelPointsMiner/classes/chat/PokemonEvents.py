from datetime import datetime
from dateutil.parser import parse

from ..Utils import (
    DISCORD_ALERTS
)

from ..entities.Pokemon import get_sprite

class PokemonEvents():
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
                    self.log("green", f"A T{tier} snowman has been built in {twitch_channel}")
            except Exception as e:
                self.log("red", "not a real snowman message - " + argstring + str(e))

    def check_xmas_delibird_gift(self, client, message, argstring):
        if self.username in argstring.lower() and "Delibird drops the following" in argstring and "HolidayPresent" in argstring:
            twitch_channel = message.target[1:]

            item = argstring.split("HolidayPresent")[1].replace(":", "").strip()
            msg = f"🎁Received {item} as a present from Delibird in {twitch_channel} channel🎁"
            self.log("green", msg)
            self.pokemon.discord.post(DISCORD_ALERTS, msg)

    def check_got_dragon_egg(self):
        filtered = sorted(self.pokemon.computer.pokemon, key=lambda x: x["id"], reverse=True)[:3]

        caught = None
        caught_obj = None
        for poke in filtered:
            pokemon = self.get_pokemon_stats(poke["pokedexId"])
            if pokemon.is_egg is False:
                continue

            if (datetime.utcnow() - parse(poke["caughtAt"][:-1])).total_seconds() > 60 * 5:
                continue

            caught = poke
            caught_obj = pokemon
            break

        return caught_obj, caught

    def check_egg_hatched(self, current_buddy):
        old_buddy = self.pokemon.poke_buddy
        old_buddy_obj = self.get_pokemon_stats(old_buddy["pokedexId"])
        
        if old_buddy_obj.is_egg and old_buddy["id"] != current_buddy["id"]:
            current_buddy_obj = self.get_pokemon_stats(current_buddy["pokedexId"])

            ivs = int(current_buddy.get("avgIV", 0))
            lvl = current_buddy.get("lvl", 0)
            shiny = " Shiny" if current_buddy.get("isShiny", False) else ""
            egg = old_buddy_obj.name
            msg = f"🥚{egg} hatched into a{shiny} {current_buddy_obj.name} ({current_buddy_obj.tier}) Lvl.{lvl} {ivs}IV🥚"

            self.log("green", msg)
            if self.pokemon.settings["alert_egg_hatched"]:
                buddy_sprite = get_sprite("pokemon", str(current_buddy["pokedexId"]), shiny=current_buddy.get("isShiny", False))
                self.pokemon.discord.post(DISCORD_ALERTS, msg, file=buddy_sprite)

    def check_pokebuddy(self, cached=False):
        if cached is False:
            all_pokemon = self.pokemon_api.get_all_pokemon()
            self.pokemon.sync_computer(all_pokemon)

        all_pokemon = self.pokemon.computer.pokemon
        for pokemon in all_pokemon:
            if pokemon["isBuddy"]:
                if self.pokemon.poke_buddy is not None:
                    self.check_egg_hatched(pokemon)
                self.pokemon.poke_buddy = pokemon
                break

        if self.pokemon.settings["hatch_eggs"]:
            self.hatch_egg()

    def hatch_egg(self):
        buddy = self.pokemon.poke_buddy

        # make sure if have egg its buddy
        if buddy is not None:
            # check if already hatching an egg
            pokemon = self.get_pokemon_stats(buddy["pokedexId"])
            if pokemon.is_egg:
                # already hatching egg
                return

        all_pokemon = self.pokemon.computer.pokemon
        potential_eggs = [pokemon for pokemon in all_pokemon if pokemon["name"].lower().endswith(" egg")]
        for egg in potential_eggs:
            pokemon = self.get_pokemon_stats(egg["pokedexId"])
            # 999002 is ranked battle egg, can't auto hatch so ignore
            if pokemon.is_egg and pokemon.pokedex_id != 999002:
                self.set_buddy(egg)
                return
