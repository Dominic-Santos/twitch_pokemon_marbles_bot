
VALID_TYPES = ['Bug', 'Dark', 'Dragon', 'Electric', 'Fairy', 'Fighting', 'Fire', 'Flying', 'Ghost', 'Grass', 'Ground', 'Ice', 'Normal', 'Poison', 'Psychic', 'Rock', 'Steel', 'Water']


class Missions(object):
    def __init__(self):
        self.data = {}
        self.prev_data = {}
        self.prev_progress = {}
        self.progress = {}
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
                "item_amount": mission["rewardItem"]["amount"]
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
                if mission_unique not in self.prev_data and self.initial is False:
                    # new mission detected
                    if self.skip_default:
                        self.skip.append(mission_unique)
                    new_missions.append(mission)

                mission_title = mission["name"].lower().replace("[flash]", " ").replace("[event]", " ").replace("é", "e").replace("wonder trade", "wondertrade").strip()
                mission_title = "".join([c for c in mission_title if c.isalnum() or c == " "]).strip()
                mission_title = " ".join([w for w in mission_title.split(" ") if w != ""])

                if mission_title.startswith("wondertrade"):
                    if mission_title == "wondertrade":
                        # just wondertrade anything does not require a mission
                        pass
                    elif "level" in mission_title or "lvl" in mission_title:
                        the_level = int("".join([c for c in mission_title if c.isnumeric()]))
                        if "higher" in mission_title:
                            self.data.setdefault("wondertrade_level", []).append((the_level, 9999))
                        else:
                            self.data.setdefault("wondertrade_level", []).append((0, the_level))
                    elif " fish " in mission_title:
                        self.data["wondertrade_fish"] = True
                    elif " cat " in mission_title:
                        self.data["wondertrade_cat"] = True
                    elif " dog " in mission_title:
                        self.data["wondertrade_dog"] = True
                    elif "bst" in mission_title:
                        the_bst = int("".join([c for c in mission_title if c.isnumeric()]))
                        if "less than" in mission_title:
                            self.data.setdefault("wondertrade_bst", []).append((0, the_bst))
                        else:
                            self.data.setdefault("wondertrade_bst", []).append((the_bst, 9999))
                    elif "kg" in mission_title:
                        pass
                    else:
                        the_type = mission_title.split(" ")[1].title()
                        self.data.setdefault("wondertrade_type", []).append(the_type)
                elif "stadium" in mission_title:
                    if "easy" in mission_title:
                        self.data["stadium"] = "easy"
                    elif "medium" in mission_title:
                        self.data["stadium"] = "medium"
                    elif "hard" in mission_title:
                        self.data["stadium"] = "hard"
                elif " fish " in mission_title:
                    self.data["fish"] = True
                elif " cat " in mission_title:
                    self.data["cat"] = True
                elif " dog " in mission_title:
                    self.data["dog"] = True
                elif "miss" in mission_title:
                    miss_list = mission_title.split(" ")
                    just_miss = True
                    if len(miss_list) > 2:
                        the_type = miss_list[1].title()
                        if the_type in VALID_TYPES:
                            just_miss = False

                    if just_miss:
                        self.data["miss"] = True
                    else:
                        self.data.setdefault("miss_type", []).append(the_type)
                elif mission_title == "attempt catches":
                    self.data["attempt"] = True
                elif mission_title.startswith("catch"):
                    if "kg" in mission_title:
                        the_kg = int("".join([c for c in mission_title.split("kg")[0] if c.isnumeric()]))
                        if "heavier than" in mission_title:
                            self.data.setdefault("weight", []).append((the_kg, 9999))
                        else:
                            self.data.setdefault("weight", []).append((0, the_kg))
                    elif "bst" in mission_title:
                        the_bst = int("".join([c for c in mission_title if c.isnumeric()]))
                        if "under" in mission_title or "less" in mission_title:
                            self.data.setdefault("bst", []).append((0, the_bst))
                        else:
                            self.data.setdefault("bst", []).append((the_bst, 9999))
                    elif "with" in mission_title:
                        ball = mission_title.split("ball")[0].strip().split(" ")[-1]
                        self.data.setdefault("ball", []).append(ball)
                    elif "mono" in mission_title:
                        self.data["monotype"] = True
                    else:
                        the_type = mission_title.split(" ")[1].title()
                        self.data.setdefault("type", []).append(the_type)
            except Exception as e:
                print(mission["name"], "parse fail", str(e))

        if len(new_missions) > 0:
            self.new_missions_callback(new_missions)

        self.initial = False

    def have_mission(self, mission_name):
        return mission_name in self.data

    def _types_mission(self, mission_name, pokemon_types):
        to_ret = []
        if self.have_mission(mission_name):
            missions = self.data.get(mission_name)

            for pokemon_type in pokemon_types:
                if pokemon_type in missions:
                    to_ret.append(pokemon_types)

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

    def check_weight_mission(self, weight):
        return self._between_mission("weight", weight)

    def check_bst_mission(self, bst):
        return self._between_mission("bst", bst)

    def check_ball_mission(self):
        return self.have_mission("ball")

    def check_monotype_mission(self):
        return self.have_mission("monotype")

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

        return reasons

    def mission_best_ball(self, mission):
        return mission not in ["attempt", "miss", "spend_money", "ball"] or mission.startswith("miss_type") or mission.startswith("stones")
