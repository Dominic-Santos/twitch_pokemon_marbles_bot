import json

LOYALTY_FILE = "pokemon_loyalty.txt"
LOYALTY_DATA = "pokemon_loyalty_data.json"

LOYALTY = {
    0: {
        1: {"limit": 100, "reward": "Increased stone drop chance by 5%"},
        2: {"limit": 250, "reward": "Catch Pokemon up to level 25"},
        3: {"limit": 500, "reward": "Chance to find rare Candy when attempting to catch"},
        4: {"limit": 1000, "reward": "3% increased shiny chance"}
    },
    1: {
        1: {"limit": 100, "reward": "Earn additional 5% $"},
        2: {"limit": 200, "reward": "Chance to obtain a golden ticket"},
        3: {"limit": 400, "reward": "Catch Pokemon up to level 25"},
        4: {"limit": 800, "reward": "Increased stone drop chance by 5%"},
        5: {"limit": 1200, "reward": "Chance to find rare Candy when attempting to catch Pokemon"},
        6: {"limit": 2000, "reward": "+3% Higher catch chance"},
        7: {"limit": 3000, "reward": "5% increased shiny chance"},
        8: {"limit": 4000, "reward": "Earn additional 5% $"},
    },
    2: {
        1: {"limit": 25, "reward": "Earn additional 5% $"},
        2: {"limit": 50, "reward": "Chance to obtain a golden ticket"},
        3: {"limit": 100, "reward": "Catch Pokemon up to level 25"},
        4: {"limit": 200, "reward": "Increased stone drop chance by 5%"},
        5: {"limit": 300, "reward": "Chance to find rare Candy when attempting to catch Pokemon"},
        6: {"limit": 500, "reward": "+3% Higher catch chance"},
        7: {"limit": 750, "reward": "5% increased shiny chance"},
        8: {"limit": 1000, "reward": "Earn additional 5% $"},
    }
}


class Loyalty(object):
    def __init__(self):
        self.loyalty_data = {}
        self.channel_list = []
        self.up_to_date = []
        self.load_loyalty()

    def save_loyalty(self):
        with open(LOYALTY_DATA, "w") as f:
            f.write(json.dumps(self.loyalty_data, indent=4))

    def load_loyalty(self):
        try:
            with open(LOYALTY_DATA, "r") as f:
                data = json.load(f)
        except:
            data = {}

        for channel in data:
            self.set_loyalty(channel, data[channel]["level"], data[channel]["points"], data[channel]["limit"], save=False)
            # check if got all possible rewards
            loyalty = self.get_loyalty(self.loyalty_data[channel]["level"], self.loyalty_data[channel]["featured"])
            if loyalty is None:
                self.up_to_date.append(channel)

    def need_loyalty(self, channel):
        return channel not in self.up_to_date

    def set_loyalty(self, channel, loyalty_level, current_points, level_points, save=True):
        if channel in ["jonaswagern", "deemonrider"]:
            featured_channel = 1
        elif (
            level_points == 250
        ) or (
            level_points == 100 and loyalty_level == 1
        ) or (
            level_points == 500 and loyalty_level == 3
        ) or (
            level_points == 1000 and loyalty_level == 4
        ):
            featured_channel = 0
        else:
            featured_channel = 2

        self.loyalty_data[channel] = {
            "featured": featured_channel,
            "level": loyalty_level,
            "points": current_points,
            "limit": level_points
        }

        if save:
            if channel not in self.up_to_date:
                self.up_to_date.append(channel)
            self.output_loyalty()

    def get_loyalty(self, level, featured):
        return LOYALTY.get(featured, {}).get(level, None)

    def get_highest_loyalty_channel(self):
        all_channels = sorted(
            [(key, values) for key, values in self.loyalty_data.items() if key in self.channel_list],
            key=lambda x: (0 - x[1]["featured"], 0 - x[1]["points"])
        )

        if len(all_channels) == 0:
            return None

        return all_channels[0][0]

    def increment_loyalty(self, channel):
        to_return = None

        if channel in self.loyalty_data:
            self.loyalty_data[channel]["points"] = self.loyalty_data[channel]["points"] + 1
            if self.loyalty_data[channel]["points"] == self.loyalty_data[channel]["limit"]:
                loyalty = self.get_loyalty(self.loyalty_data[channel]["level"], self.loyalty_data[channel]["featured"])
                current_reward = loyalty["reward"]

                next_level = self.get_loyalty(self.loyalty_data[channel]["level"] + 1, self.loyalty_data[channel]["featured"])

                if next_level is not None:
                    self.loyalty_data[channel]["level"] = self.loyalty_data[channel]["level"] + 1
                    self.loyalty_data[channel]["limit"] = next_level["limit"]
                    next_reward = next_level["reward"]
                else:
                    self.loyalty_data[channel]["limit"] = None
                    next_reward = None

                to_return = [current_reward, next_reward]

            # these 2 channels are joined
            if channel == "jonaswagern" or channel == "deemonrider":
                new_channel = "deemonrider" if channel == "jonaswagern" else "jonaswagern"
                self.loyalty_data[new_channel] = self.loyalty_data[channel]

            self.output_loyalty()

        return to_return

    def output_loyalty(self):
        self.save_loyalty()
        self.save_loyalty_readable()

    def save_loyalty_readable(self):
        to_output = sorted(
            [(key, values) for key, values in self.loyalty_data.items()],
            key=lambda x: (0 - x[1]["featured"], 0 - x[1]["points"])
        )
        with open(LOYALTY_FILE, "w") as output:
            for channel, data in to_output:
                featured = data["featured"]
                level = data["level"]
                points = data["points"]
                limit = data["limit"]
                output.write(f"{featured} - {channel} - level {level} - {points}/{limit}\n")
