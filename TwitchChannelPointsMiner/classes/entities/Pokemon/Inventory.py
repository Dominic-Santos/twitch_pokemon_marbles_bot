from .Pokedex import POKEMON_TYPES

CATCH_BALL_PRIORITY = ["ultraball", "greatball", "pokeball", "premierball"]
CATCH_BALL_TIERS = ["S", "A", "B", "C", "C"]
CATCH_BALL_RATES = {
    "ultraball": 80,
    "greatball": 55,
    "pokeball": 30,
    "premierball": 30
}


class Inventory(object):
    def __init__(self):
        # updated from config by PCG
        self.use_special_balls = True
        self.spend_money_strategy = "save"
        self.money_saving = 0

        self.reset()

    def reset(self):
        self.cash = 0
        self.balls = {}
        self.items = {}
        self.special_balls = {}
        self.other_balls = {}
        self.ball_catch_rates = {}

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
                        try:
                            self.ball_catch_rates[ball] = int(item["catchRate"].replace("%", ""))
                        except:
                            pass

                # Balls for fish pokemon
                if "Fish" in item["description"]:
                    if "Fish" not in self.other_balls:
                        self.other_balls["Fish"] = []
                    self.other_balls["Fish"].append(ball)

            self.items[item["name"].lower()] = {
                "name": item["name"],
                "sprite": item["sprite_name"],
                "amount": item["amount"],
                "category": item["category"]
            }

    def get_item(self, item_name):
        return self.items.get(item_name.lower(), None)

    def have_item(self, item_name):
        the_item = self.get_item(item_name)
        return the_item is not None and the_item["amount"] > 0

    def use_item(self, item_name):
        name = item_name.lower()
        if self.have_item(name):
            self.items[name]["amount"] = self.items[name]["amount"] - 1

    # ##### Balls ####

    def _get_strategy(self, catch_reasons, mission_balls):

        reasons = [reason.split(" (")[0] for reason in catch_reasons]

        if len(reasons) == 1 and "spend_money" in reasons:
            # if the only reason is to spend money, then apply the selected strategy
            return self.spend_money_strategy, None

        for reason in reasons:
            if reason not in ["attempt", "miss", "spend_money", "ball", "shiny_hunt", "miss_type", "stones"]:
                return "best", None

        for catch_ball in mission_balls:
            ball = catch_ball + "ball"
            if self.have_ball(ball):
                return "force", ball

        if "shiny_hunt" in reasons:
            for ball in ["ultracherishball", "greatcherishball", "cherishball"]:
                if self.have_ball(ball):
                    return "force", ball
            return "best", None

        if len([x for x in reasons if x.startswith("stones")]) > 0:
            if self.have_ball("stoneball"):
                return "force", "stoneball"
            else:
                return "best", None

        return "worst", None

    def get_strategy(self, reasons, mission_balls):
        strategy, ball = self._get_strategy(reasons, mission_balls)

        if strategy == "best":
            if self.cash < self.money_saving:
                strategy = "save"

        return strategy, ball

    def is_repeat(self, reasons):
        for reason in ["pokedex", "alt", "special"]:
            if reason in reasons:
                return False
        return True

    def get_catch_ball(self, pokemon, reasons, mission_balls=[]):
        repeat = self.is_repeat(reasons)

        strategy, ball = self.get_strategy(reasons, mission_balls)
        if ball is not None:
            return ball

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
            # 90% catch rate
            if self.have_ball("timerball"):
                yield "timerball"

            if self.have_ball("quickball"):
                yield "quickball"

            # 80% catch rate
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
                if self.have_ball("featherball"):
                    yield "featherball"

        type_balls = []
        if self.use_special_balls:
            if pokemon.types is not None:
                for t in sorted(pokemon.types):
                    if t in self.special_balls:
                        for ball in self.special_balls[t]:
                            type_balls.append(ball)

        type_balls = sorted(type_balls, key=lambda x: self.ball_catch_rates.get(x, 0), reverse=True)

        prev_catch_rate = 100
        for ball in CATCH_BALL_PRIORITY + ["noball"]:
            catch_rate = CATCH_BALL_RATES.get(ball, 0)

            type_balls_part = [x for x in type_balls if self.ball_catch_rates.get(x, 0) in range(catch_rate, prev_catch_rate)]

            for b in type_balls_part:
                yield b

            if self.have_ball(ball):
                yield ball

            prev_catch_rate = catch_rate

    def have_ball(self, ball):
        return self.balls.get(ball, 0) > 0
