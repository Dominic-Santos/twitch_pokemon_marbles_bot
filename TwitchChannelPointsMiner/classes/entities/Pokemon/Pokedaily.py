import re


class Message(object):
    def __init__(self):
        self.valid = False
        self.repeat = False
        self.last_redeemed = {
            "hours": 0,
            "minutes": 0,
            "seconds": 0
        }
        self.rewards = []
        self.rarity = "unknown"

    def __str__(self):
        return f"Pokedaily Message: valid={self.valid}, repeat={self.repeat}, last_redeemed={self.last_redeemed}, rarity={self.rarity}, rewards={self.rewards}"

    def set_last_redeemed(self, hours, minutes, seconds):
        self.last_redeemed.update({
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds
        })

    def add_last_redeemed(self, seconds):
        hours = int(seconds // 3600)
        seconds = seconds - (hours * 3600)

        minutes = int(seconds // 60)
        seconds = seconds - (minutes * 60)

        seconds = int(seconds // 1)

        self.last_redeemed["hours"] = self.last_redeemed["hours"] + hours
        self.last_redeemed["minutes"] = self.last_redeemed["minutes"] + minutes
        self.last_redeemed["seconds"] = self.last_redeemed["seconds"] + seconds

        if self.last_redeemed["seconds"] >= 60:
            mins = self.last_redeemed["seconds"] // 60
            self.last_redeemed["seconds"] = self.last_redeemed["seconds"] - mins * 60
            self.last_redeemed["minutes"] = self.last_redeemed["minutes"] + mins

        if self.last_redeemed["minutes"] >= 60:
            hours = self.last_redeemed["minutes"] // 60
            self.last_redeemed["minutes"] = self.last_redeemed["minutes"] - hours * 60
            self.last_redeemed["hours"] = self.last_redeemed["hours"] + hours


def parse_next_available(content):
    if "You already have claimed" not in content:
        return 0

    # already claimed this one
    time_content = content.split("Please come back in ")[1].split(".")[0]

    result = re.findall(r'\d{1,}', time_content)
    hours = 0
    minutes = 0
    seconds = 0

    if "hour" in time_content:
        hours = int(result.pop(0))
    if "minute" in time_content:
        minutes = int(result.pop(0))
    if "second" in time_content:
        seconds = int(result.pop(0))

    return hours * 60 * 60 + minutes * 60 + seconds


def parse_message(content):
    message = Message()

    if "You already have claimed" in content:
        # already claimed this one
        message.repeat = True
        message.valid = True

        time_content = content.split("Please come back in ")[1].split(".")[0]

        result = re.findall(r'\d{1,}', time_content)
        hours = 19
        minutes = 59
        seconds = 60

        if "hour" in time_content:
            hours = hours - int(result.pop(0))
        if "minute" in time_content:
            minutes = minutes - int(result.pop(0))
        if "second" in time_content:
            seconds = seconds - int(result.pop(0))

        if seconds == 60:
            minutes = minutes + 1
            seconds = 0

        if minutes == 60:
            hours = hours + 1
            minutes = 0

        message.set_last_redeemed(hours, minutes, seconds)

    if "rarity_" in content:
        message.valid = True
        message.rarity = content.split("rarity_")[1].split(":")[0]

        rewards = ":".join(content.split("reward")[-1].split(":")[1:])

        # get rid of roles
        results = set(re.findall(r'<:[^:]*:\d{5,}>', rewards))
        for result in results:
            rewards = rewards.replace(result, "")

        # get rid of rarity
        rewards = rewards.replace(":rarity_{}:".format(message.rarity), "")

        items = rewards.split("\n")
        items = [item.strip().split(":")[-1].strip() for item in items if item.strip() != ""]
        message.rewards = items

    return message
