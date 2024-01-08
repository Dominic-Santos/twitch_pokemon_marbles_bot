from .Pokedex import POKEMON_TYPES, POKEMON_ATTRIBUTES

MISSION_REASONS = ["type", "weight", "bst", "fish", "dog", "cat", "miss", "miss_type", "attempt", "ball", "monotype", "event", "catch"]

BIGGER_SYNONIMS = ["greater", "above", "higher", "larger", "heavier", "over", "more than"]


def bigger_smaller(mission_title, bigger, smaller):
    for word in BIGGER_SYNONIMS:
        if word in mission_title:
            return bigger
    return smaller


class Missions(object):
    def __init__(self):
        self.data = {}
        self.prev_data = {}
        self.prev_progress = {}
        self.progress = {}
        self.event = []
        self.skip = []
        self.skip_default = False
        self.initial = True

    def reset(self):
        self.prev_progress = self.progress
        self.prev_data = self.data
        self.progress = {}
        self.data = {}

    def new_missions_callback(self, *args):
        pass

    @staticmethod
    def get_reward(mission):
        if mission["rewardItem"] is not None:
            amount = "" if mission["rewardItem"]["amount"] == 0 else "%s " % mission["rewardItem"]["amount"]
            item = mission["rewardItem"]["name"]
            reward = {
                "reward_type": mission["rewardItem"]["category"],
                "reward_name": mission["rewardItem"]["sprite_name"],
                "reward": f"{amount}{item}",
                "item_name": item,
                "item_amount": mission["rewardItem"]["amount"],
                "tm_type": mission["rewardItem"]["tmType"]
            }
        else:
            reward = {
                "reward_type": "pokemon",
                "reward_name": mission["rewardPokemon"]["id"],
                "reward": mission["rewardPokemon"]["name"]
            }
        return reward

    def add_progress(self, mission):
        reward = self.get_reward(mission)
        goal = mission["goal"]
        title = mission["name"]
        progress = mission["progress"]
        progress_key = self.get_unique_id(mission)

        self.progress[progress_key] = {
            "title": f"{title} ({goal})",
            "goal": goal,
            "progress": progress,
            "reward": reward
        }

    def get_completed(self):
        completed = []
        for progress_title, progress_data in self.progress.items():
            # check if mission is done
            if progress_data["goal"] > progress_data["progress"]:
                continue

            # check if had the mission before
            previous_data = self.prev_progress.get(progress_title, None)
            if previous_data is None:
                continue

            # check if mission was done before
            if previous_data["goal"] <= previous_data["progress"]:
                continue

            completed.append((progress_data["title"], progress_data["reward"]))

        return completed

    @staticmethod
    def get_unique_id(mission):
        unique_id = mission["name"] + "_" + str(mission["goal"])
        if mission["rewardItem"] is None:
            unique_id = unique_id + "_" + str(mission["rewardPokemon"]["id"])
        else:
            unique_id = unique_id + "_" + str(mission["rewardItem"]["id"]) + "_" + str(mission["rewardItem"]["amount"])
        return unique_id

    def set(self, missions):
        new_missions = []
        self.reset()

        for mission in missions["missions"]:
            self.add_progress(mission)

            if mission["progress"] >= mission["goal"]:
                continue
            try:
                mission_unique = self.get_unique_id(mission)
                if mission_unique in self.skip:
                    continue

                detected_mission = self.parse_mission(mission)

                if detected_mission is None:
                    mission["detected"] = "unknown"
                else:
                    mission["detected"] = f"{detected_mission[0]} {str(detected_mission[2])}"
                    if detected_mission[1]:
                        self.data.setdefault(detected_mission[0], []).append(detected_mission[2])
                    else:
                        self.data[detected_mission[0]] = detected_mission[2]

                if mission_unique not in self.prev_progress and self.initial is False:
                    # new mission detected
                    if self.skip_default:
                        self.skip.append(mission_unique)
                    new_missions.append(mission)
            except Exception as e:
                print(mission["name"], "parse fail", str(e))

        if len(new_missions) > 0:
            self.new_missions_callback(new_missions)

        self.initial = False

    def parse_mission(self, mission):
        # returns (key, is_array, value) // None if error or unknown missions
        try:
            mission_title = mission["name"].lower().replace("[flash]", " ").replace("[event]", " ").replace("é", "e").replace("wonder trade", "wondertrade").strip()
            mission_title = "".join([c for c in mission_title if c.isalnum() or c == " "]).strip()
            mission_title = " ".join([w for w in mission_title.split(" ") if w != ""])

            if mission_title.startswith("wondertrade"):
                if mission_title == "wondertrade":
                    return ("wondertrade", False, True)
                elif "level" in mission_title or "lvl" in mission_title:
                    the_level = int("".join([c for c in mission_title if c.isnumeric()]))
                    return bigger_smaller(
                        mission_title,
                        ("wondertrade_level", True, (the_level, 9999)),
                        ("wondertrade_level", True, (0, the_level))
                    )
                elif " fish " in mission_title:
                    return ("wondertrade_fish", False, True)
                elif " cat " in mission_title:
                    return ("wondertrade_cat", False, True)
                elif " dog " in mission_title:
                    return ("wondertrade_dog", False, True)
                elif "bst" in mission_title:
                    the_bst = int("".join([c for c in mission_title if c.isnumeric()]))
                    return bigger_smaller(
                        mission_title,
                        ("wondertrade_bst", True, (the_bst, 9999)),
                        ("wondertrade_bst", True, (0, the_bst))
                    )
                elif "kg" in mission_title:
                    pass
                else:
                    the_type = mission_title.split(" ")[1].title()
                    return ("wondertrade_type", True, the_type)
            elif "stadium" in mission_title:
                if "easy" in mission_title:
                    return ("stadium", False, "easy")
                elif "medium" in mission_title:
                    return ("stadium", False, "medium")
                elif "hard" in mission_title:
                    return ("stadium", False, "hard")
            elif " fish " in mission_title:
                return ("fish", False, True)
            elif " cat " in mission_title:
                return ("cat", False, True)
            elif " dog " in mission_title:
                return ("dog", False, True)
            elif "miss" in mission_title:
                for the_type in POKEMON_TYPES:
                    if the_type.lower() in mission_title:
                        return ("miss_type", True, the_type)
                return ("miss", False, True)
            elif mission_title == "attempt catches":
                return ("attempt", False, True)
            elif mission_title.startswith("catch"):
                if mission_title == "catch a pokemon" or mission_title == "catch pokemon":
                    return ("catch", False, True)
                elif "event" in mission_title:
                    return ("event", False, True)
                elif "kg" in mission_title or "weight" in mission_title:
                    the_kg = int("".join([c for c in mission_title.split("kg")[0] if c.isnumeric()]))
                    return bigger_smaller(
                        mission_title,
                        ("weight", True, (the_kg, 9999)),
                        ("weight", True, (0, the_kg))
                    )
                elif "bst" in mission_title:
                    the_bst = int("".join([c for c in mission_title if c.isnumeric()]))
                    return bigger_smaller(
                        mission_title,
                        ("bst", True, (the_bst, 9999)),
                        ("bst", True, (0, the_bst))
                    )
                elif "with" in mission_title:
                    ball = mission_title.split("ball")[0].strip().split(" ")[-1]
                    return ("ball", True, ball)
                elif "mono" in mission_title:
                    return ("monotype", False, True)
                elif "type" in mission_title:
                    # ex: catch fire type pokemon
                    the_type = mission_title.split(" ")[1].title()
                    return ("type", True, the_type)
                else:
                    # ex: catch fire pokemon
                    the_maybe_type = mission_title.replace("catch", "").replace("pokemon", "").strip().title()
                    if the_maybe_type in POKEMON_TYPES:
                        return ("type", True, the_maybe_type)
        except Exception as e:
            print(mission["name"], "parse fail", str(e))
        return None

    def have_mission(self, mission_name):
        return mission_name in self.data

    def _types_mission(self, mission_name, pokemon_types):
        to_ret = []
        if self.have_mission(mission_name):
            missions = self.data.get(mission_name)

            for pokemon_type in pokemon_types:
                if pokemon_type in missions:
                    to_ret.append(pokemon_type)

        return to_ret

    def _between_mission(self, mission_name, unit):
        if self.have_mission(mission_name):
            missions = self.data.get(mission_name)

            for m_min, m_max in missions:
                if unit > m_min and unit < m_max:
                    return True

        return False

    # ##### Stadium Missions ####
    def check_stadium_mission(self):
        return self.have_mission("stadium")

    def check_stadium_difficulty(self):
        return self.data.get("stadium", "easy")

    # ##### Wondertrade Missions #####
    def check_wondertrade_type_mission(self, pokemon_types):
        return self._types_mission("wondertrade_type", pokemon_types)

    def check_wondertrade_bst_mission(self, bst):
        return self._between_mission("wondertrade_bst", bst)

    def check_wondertrade_level_mission(self, level):
        return self._between_mission("wondertrade_level", level)

    def check_all_wondertrade_missions(self, pokemon):
        reasons = []
        for pokemon_type in self.check_wondertrade_type_mission(pokemon.types):
            reasons.append(f"type ({pokemon_type.title()})")

        if self.check_wondertrade_bst_mission(pokemon.bst):
            reasons.append("bst")

        if self.check_wondertrade_level_mission(pokemon.level):
            reasons.append("level")

        if pokemon.is_fish and self.have_mission("wondertrade_fish"):
            reasons.append("fish")

        if pokemon.is_cat and self.have_mission("wondertrade_cat"):
            reasons.append("cat")

        if pokemon.is_dog and self.have_mission("wondertrade_dog"):
            reasons.append("dog")
        return reasons

    def have_wondertrade_missions(self):
        if self.have_mission("wondertrade_type"):
            return True
        elif self.have_mission("wondertrade_bst"):
            return True
        elif self.have_mission("wondertrade_level"):
            return True
        elif self.have_mission("wondertrade_fish"):
            return True
        elif self.have_mission("wondertrade_dog"):
            return True
        elif self.have_mission("wondertrade_cat"):
            return True
        return False

    # ##### Regular Missions #####

    def check_type_mission(self, pokemon_types):
        return self._types_mission("type", pokemon_types)

    def check_fish_mission(self):
        return self.have_mission("fish")

    def check_dog_mission(self):
        return self.have_mission("dog")

    def check_cat_mission(self):
        return self.have_mission("cat")

    def check_miss_mission(self):
        return self.have_mission("miss")

    def check_miss_type_mission(self, pokemon_types):
        return self._types_mission("miss_type", pokemon_types)

    def check_attempt_mission(self):
        return self.have_mission("attempt")

    def check_catch_mission(self):
        return self.have_mission("catch")

    def check_weight_mission(self, weight):
        return self._between_mission("weight", weight)

    def check_bst_mission(self, bst):
        return self._between_mission("bst", bst)

    def check_ball_mission(self):
        return self.have_mission("ball")

    def check_monotype_mission(self):
        return self.have_mission("monotype")

    def check_event_pokemon(self, pokemon):
        to_ret = []
        for pokemon_type in pokemon.types:
            if pokemon_type in self.event:
                to_ret.append(pokemon_type)

        for att in POKEMON_ATTRIBUTES:
            if att in self.event and getattr(pokemon, "is_" + att.lower()):
                to_ret.append(att)
        return to_ret

    def check_event_mission(self, pokemon):
        if self.have_mission("event"):
            return self.check_event_pokemon(pokemon)

        return []

    def check_all_missions(self, pokemon):
        reasons = []
        for pokemon_type in self.check_type_mission(pokemon.types):
            reasons.append(f"type ({pokemon_type.title()})")

        if self.check_weight_mission(pokemon.weight):
            reasons.append("weight")

        if self.check_bst_mission(pokemon.bst):
            reasons.append("bst")

        if pokemon.is_fish and self.check_fish_mission():
            reasons.append("fish")

        if pokemon.is_dog and self.check_dog_mission():
            reasons.append("dog")

        if pokemon.is_cat and self.check_cat_mission():
            reasons.append("cat")

        if self.check_miss_mission():
            reasons.append("miss")

        for pokemon_type in self.check_miss_type_mission(pokemon.types):
            reasons.append(f"miss_type ({pokemon_type.title()})")

        if self.check_attempt_mission():
            reasons.append("attempt")

        if self.check_ball_mission():
            reasons.append("ball")

        if len(pokemon.types) == 1 and self.check_monotype_mission():
            reasons.append("monotype")

        if self.check_catch_mission():
            reasons.append("catch")

        for pokemon_type in self.check_event_mission(pokemon):
            reasons.append(f"event ({pokemon_type.title()})")

        return reasons
