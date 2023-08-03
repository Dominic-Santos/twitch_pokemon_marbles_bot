
class Pokemon(object):
    def __init__(self, data={}):
        self.name = data.get("name", "NA")
        self.weight = data.get("weight", 0)
        self.pokedex_id = data.get("pokedex_id", 0)
        self.tier = data.get("tier", "NA")
        self.types = [t for t in [data.get("type1", "none").title(), data.get("type2", "none").title()] if t != "None"]

        base_stats = data.get("base_stats", {})
        self.hp = base_stats.get("hp", 0)
        self.speed = base_stats.get("speed", 0)
        self.attack = base_stats.get("attack", 0)
        self.defense = base_stats.get("defense", 0)
        self.special_attack = base_stats.get("special_attack", 0)
        self.special_defense = base_stats.get("special_defense", 0)

        # not currently used
        self.description = data.get("description", "")
        self.generation = data.get("generation", 0)

        self.is_fish = False
        self.is_baby = False
        self.is_starter = False
        self.is_legendary = False
        self.is_female = False

        # evolution data, None = hasnt been added yet
        self.evolve_to = data.get("evolves_to", None)
        self.evolve_from = data.get("evolves_from", [])

        # fields for bag pokemon
        self.level = 0

    @property
    def bst(self):
        return self.hp + self.speed + self.attack + self.defense + self.special_attack + self.special_defense

    def __str__(self):
        return f"{self.pokedex_id} {self.name}, {self.bst}BST, {self.weight}KG, tier {self.tier}, types {self.types}"
