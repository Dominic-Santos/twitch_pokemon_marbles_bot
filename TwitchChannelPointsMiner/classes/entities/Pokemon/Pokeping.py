import re
from dateutil.parser import parse

from .Pokemon import Pokemon
from .Utils import save_to_json

POKEPING_CHANNEL = "935704401954349196"
GUILD_ID = 935702835771883620
ROLE_REGEX = r'<@&\d{5,}>'

POKEMON_SPECIAL_ALTS = ["Minior", "Vivillon", "Aegislash", "Rotom"]
POKEMON_WITH_ALTERNATE_VERSIONS = ["Abomasnow", "Aegislash", "Aipom", "Alcremie", "Ambipom", "Appletun", "Arcanine", "Basculegion", "Basculin", "Beautifly", "Bibarel", "Bidoof", "Blaziken", "Braviary", "Buizel", "Burmy", "Butterfree", "Cacturne", "Camerupt", "Castform", "Centiskorch", "Charizard", "Cherrim", "Coalossal", "Combee", "Croagunk", "Darmanitan", "Deerling", "Diglett", "Donphan", "Dugtrio", "Dustox", "Exeggutor", "Finneon", "Frillish", "Gabite", "Garchomp", "Geodude", "Gible", "Girafarig", "Gligar", "Golbat", "Golem", "Goodra", "Gourgeist", "Graveler", "Grimer", "Growlithe", "Gulpin", "Heracross", "Hippowdon", "Houndoom", "Indeedee", "Jellicent", "Kricketot", "Krikcetune", "Ledian", "Ledyba", "Lilligant", "Ludicolo", "Lumineon", "Luxio", "Luxray", "Lycanroc", "Magikarp", "Magnemite", "Mamoswine", "Marowak", "Meditite", "Meowstic", "Meowth", "Milotic", "Minior", "Morpeko", "Mr-Mime", "Muk", "Murkrow", "Ninetales", "Numel", "Nuzleaf", "Octillery", "Orbeetle", "Oricorio", "Overqwil", "Pachirisu", "Palossand", "Persian", "Pikachu", "Piloswine", "Politoed", "Polteageist", "Ponyta", "Pumpkaboo", "Pyroar", "Quagsire", "Raichu", "Rapidash", "Raticate", "Rattata", "Relicanth", "Rhydon", "Rhyperior", "Rockruff", "Roselia", "Roserade", "Rotom", "Sandaconda", "Sandshrew", "Sandslash", "Sawsbuck", "Scizor", "Scyther", "Shellos", "Shiftry", "Shinx", "Sinistea", "Slowbro", "Vivillon", "Voltorb", "Vulpix", "Weavile", "Weezing", "Wishiwashi", "Wobbuffet", "Wooper", "Wormadam", "Xatu", "Yamask", "Zigzagoon", "Zoroark", "Zorua", "Zubat"]

# rotom have version after with no parenthesis
# minior & vivillon no clue on which one
# lycanroc & aegislash has the ()


class Pokeping(object):
    def __init__(self):
        self.discord = None
        self.roles = {}
        self.alter_role = "0"

    def set_discord(self, discord):
        self.discord = discord

    def get_pokemon(self):
        messages = self.get_messages(2)
        pokemon = self.parse_pokemon(messages[0])
        if pokemon.is_alternate or pokemon.name == "NA":
            self.parse_pokemon(messages[1], pokemon=pokemon)
        pokemon.check_name()
        return pokemon

    @save_to_json
    def get_messages(self, limit=1):
        url = f"https://discord.com/api/v9/channels/{POKEPING_CHANNEL}/messages?limit={limit}"
        data = self.discord.get(url)
        return data

    def get_last_message(self, limit=1):
        data = self.get_messages(limit)
        data = data[-1]
        return data

    def get_roles(self):
        url = f"https://discord.com/api/v9/guilds/{GUILD_ID}/roles"
        roles = self.discord.get(url)
        self.roles = {role["id"]: role["name"] for role in roles}
        self.get_alter_role()

    def get_alter_role(self):
        self.alter_role = self.find_role("Alter")

    def find_role(self, name):
        for role_id, role_name in self.roles.items():
            if role_name == name:
                return role_id
        return None

    def parse_pokemon(self, data, pokemon=None):
        if pokemon is None:
            poke = Pokemon()
        else:
            poke = pokemon

        content = data["content"]
        result = re.findall(ROLE_REGEX, content)
        for role in result:
            content = content.replace(role, self.roles.get(role[3:-1], "?"))
        # some roles die but they forget to remove @
        content = content.replace("@", "")

        parse_alt = False

        if self.alter_role not in data["mention_roles"]:
            # should be normal pokemon message
            # some pokemon messages have ID at start
            if content.startswith("ID"):
                try:
                    poke.pokemon_id = int(content.split(":")[0][3:])
                    content = ":".join(content.split(":")[1:]).strip()
                except:
                    parse_alt = True
        else:
            parse_alt = True

        if parse_alt:
            # must parse alt message
            poke.is_alternate = True
            poke.pokemon_id = int(content.split("ID: ")[1].split(" ")[0])
            poke.alt_name = content.split("| ")[-1].split(" ")[0]
        else:
            # is normal pokemon message
            try:
                name, tier, types_and_bst, weight_and_garbage = content.split(" - ")[0:4]
                weight = weight_and_garbage.split("KG")[0]
                types = types_and_bst.split(" ")[:-1]
                bst = types_and_bst.split(" ")[-1]

                poke.name = name
                poke.tier = tier.split(":")[1].strip()
                poke.types = types
                poke.bst = int(bst.replace("BST", ""))
                poke.weight = float(weight.strip())
            except:
                pass

        # check if its a fish
        if ":fish:" in content:
            poke.is_fish = True

        poke.spawn = parse(data["timestamp"].split("+")[0])

        return poke
