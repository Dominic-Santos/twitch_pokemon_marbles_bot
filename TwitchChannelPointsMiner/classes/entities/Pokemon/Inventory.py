CATCH_BALL_PRIORITY = ["ultraball", "greatball", "pokeball", "premierball"]
CATCH_BALL_TIERS = ["S", "A", "B", "C", "C"]
POKEMON_TYPES = ["Normal", "Fighting", "Flying", "Poison", "Ground", "Rock", "Bug", "Ghost", "Steel", "Fire", "Water", "Grass", "Electric", "Psychic", "Ice", "Dragon", "Dark", "Fairy"]


class Inventory(object):
    def __init__(self):
        self.use_special_balls = True
        self.reset()

    def reset(self):
        self.cash = 0
        self.balls = {}
        self.items = {}
        self.special_balls = {}
        self.other_balls = {}

    def __str__(self):
        return "Balance: $" + str(self.cash) + " " + ", ".join(["{item}: {amount}".format(item=self.items[item]["name"], amount=self.items[item]["amount"]) for item in self.items])

    def set(self, inventory):
        self.reset()
        self.cash = inventory["cash"]
        for item in inventory["allItems"]:
            if item["category"] == "ball":
                ball = item["name"].lower().replace(" ", "")
                self.balls[ball] = item["amount"]

                for pokemon_type in POKEMON_TYPES:
                    if pokemon_type in item["description"]:
                        if pokemon_type not in self.special_balls:
                            self.special_balls[pokemon_type] = []
                        self.special_balls[pokemon_type].append(ball)

                # Balls for fish pokemon
                if "Fish" in item["description"]:
                    if "Fish" not in self.other_balls:
                        self.other_balls["Fish"] = []
                    self.other_balls["Fish"].append(ball)

            else:
                self.items[item["name"].lower()] = {
                    "name": item["name"],
                    "sprite": item["sprite_name"],
                    "amount": item["amount"],
                    "category": item["category"]
                }

    def get_item(self, item_name):
        return self.items.get(item_name.lower(), None)

    def have_item(self, item_name):
        return self.get_item(item_name) is not None

    def get_catch_ball(self, pokemon, repeat=False, strategy="best"):
        if strategy == "best":
            return self.get_catch_best_ball(pokemon, repeat)

        elif strategy == "save":
            return self.get_catch_save_ball(pokemon, repeat)

        elif strategy == "worst":
            return self.get_catch_ball_worst(pokemon, repeat)

        return None

    def get_catch_ball_worst(self, pokemon, repeat):
        ball_iter = self._recomended_balls_iter(pokemon, repeat)
        balls = [x for x in ball_iter]
        if len(balls) == 0:
            return None
        return balls[-1]

    def get_catch_best_ball(self, pokemon, repeat=False):
        ball_iter = self._recomended_balls_iter(pokemon, repeat)
        ball = self._get_next_ball(ball_iter)
        return ball

    def get_catch_save_ball(self, pokemon, repeat=False):
        ball_iter = self._recomended_balls_iter(pokemon, repeat)
        ball = self._get_next_ball(ball_iter)

        while ball is not None:
            if ball not in CATCH_BALL_PRIORITY:
                return ball

            i = CATCH_BALL_PRIORITY.index(ball)
            tiers = CATCH_BALL_TIERS[0: i + 2]
            if pokemon.tier in tiers:
                return ball

            ball = self._get_next_ball(ball_iter)

        return None

    @staticmethod
    def _get_next_ball(ball_iter):
        try:
            return next(ball_iter)
        except:
            pass
        return None

    def _recomended_balls_iter(self, pokemon, repeat=False):
        if pokemon.is_legendary and repeat is False:
            if self.have_ball("masterball"):
                yield "masterball"

        if self.use_special_balls:
            if pokemon.is_fish and "Fish" in self.other_balls:
                for ball in self.other_balls["Fish"]:
                    yield ball

            if pokemon.is_baby:
                if self.have_ball("nestball"):
                    yield "nestball"

            if repeat:
                if self.have_ball("repeatball"):
                    yield "repeatball"

            if pokemon.speed >= 100:
                if self.have_ball("fastball"):
                    yield "fastball"

            if pokemon.hp >= 100:
                if self.have_ball("healball"):
                    yield "healball"

            if pokemon.weight >= 250:
                if self.have_ball("heavyball"):
                    yield "heavyball"

            if pokemon.weight <= 5:
                if self.have_ball("feather"):
                    yield "feather"

        if self.have_ball("ultraball"):
            yield "ultraball"

        if self.use_special_balls:
            if pokemon.types is not None:
                for t in sorted(pokemon.types):
                    if t in self.special_balls:
                        for ball in self.special_balls[t]:
                            yield ball

        for ball in CATCH_BALL_PRIORITY[1:]:
            if self.have_ball(ball):
                yield ball

    def have_ball(self, ball):
        return self.balls.get(ball, 0) > 0
