from datetime import datetime
from time import sleep
import random

from ..ChatO import ClientIRC as ClientIRCO

from .ChatLogs import log
from ..Utils import (
    MARBLES_DELAY,
    MARBLES_TRIGGER_COUNT,
)

class ClientIRCMarbles(ClientIRCO):
    def __init__(self, username, token, channel, marbles):
        ClientIRCO.__init__(self, username, token, channel)
        self.init(marbles)

    def init(self, marbles):
        self.marbles = marbles
        self.marbles_timer = datetime.utcnow()
        self.marbles_counter = 0

    def on_pubmsg(self, client, message):
        if self.marbles and "!play" in " ".join(message.arguments):
            self.check_marbles(client, message)

    def check_marbles(self, client, message):
        now = datetime.utcnow()
        if (now - self.marbles_timer).total_seconds() > MARBLES_DELAY:
            self.marbles_timer = now
            self.marbles_counter = 0

        self.marbles_counter += 1

        if self.marbles_counter == MARBLES_TRIGGER_COUNT:
            sleep(random.randint(0, 60))
            client.privmsg(message.target, "!play")
            log(text=f"Joined Marbles for {message.target[1:]}")

