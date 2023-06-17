
class Pokemon(object):
    def __init__(self):
        self.name = "NA"
        self.bst = -1
        self.weight = -1
        self.pokemon_id = 0
        self.tier = "NA"
        self.types = []
        self.spawn = None

        self.is_fish = False
        self.alt_name = "NA"

    @property
    def pokedex_name(self):
        if self.name.startswith("Aegislash"):
            return "Aegislash (Shield)"
        return self.name.split("(")[0].strip()

    def check_name(self):
        if self.name.startswith("Rotom"):
            self.name = self.name.replace(" ", " (") + ")"

    def __str__(self):
        return f"{self.name}, {self.bst}BST, {self.weight}KG, tier {self.tier}, types {self.types}"

    def parse(self, data):
        self.name = data["name"]
        self.bst = sum(data["base_stats"][k] for k in data["base_stats"])
        self.tier = data["tier"]
        self.types = [data["type1"].title()]
        if data["type2"] != "none":
            self.types.append(data["type2"].title())
        self.weight = data["weight"]
        self.pokemon_id = data["pokedex_id"]
