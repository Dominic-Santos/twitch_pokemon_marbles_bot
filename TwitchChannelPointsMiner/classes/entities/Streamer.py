from ..Chat import ChatPresence, ThreadChat
from .Bet import BetSettings
from .StreamerO import StreamerSettings as StreamerSettingsO
from .StreamerO import Streamer as StreamerO


class StreamerSettings(StreamerSettingsO):
    __slots__ = [
        "make_predictions",
        "follow_raid",
        "claim_drops",
        "watch_streak",
        "bet",
        "chat",
        "marbles"
    ]

    def __init__(
        self,
        make_predictions: bool = None,
        follow_raid: bool = None,
        claim_drops: bool = None,
        claim_moments: bool = None,
        watch_streak: bool = None,
        marbles: bool = None,
        bet: BetSettings = None,
        chat: ChatPresence = None,
    ):
        super().__init__(make_predictions, follow_raid, claim_drops, claim_moments, watch_streak, bet, chat)
        self.marbles = marbles

    def default(self):
        super().default()
        if self.marbles is None:
            self.marbles = False

    def __repr__(self):
        return super().__repr__(self) + f", marbles={self.marbles})"


class Streamer(StreamerO):
    def leave_chat(self):
        if self.irc_chat is not None:
            self.irc_chat.stop()

            # Recreate a new thread to start again
            # raise RuntimeError("threads can only be started once")
            self.irc_chat = ThreadChat(
                self.irc_chat.username,
                self.irc_chat.token,
                self.username,
                self.irc_chat.channel_id,
                self.irc_chat.get_pokemoncg_token_func,
                self.irc_chat.marbles,
            )
