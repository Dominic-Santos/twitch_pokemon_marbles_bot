from .ChatO import ChatPresence as ChatPresenceO
from .ChatO import ThreadChat as ThreadChatO

from .chat.ChatLogs import log, log_file
from .chat.ChatMarbles import ClientIRCMarbles
from .chat.ChatPokemon import ClientIRCPokemon

from .Utils import (
    POKEMON,
    leave_channel,
)

class ClientIRC(ClientIRCMarbles, ClientIRCPokemon):
    def __init__(self, username, token, channel, get_pokemoncg_token, marbles, pcg):
        ClientIRCMarbles.__init__(self, username, token, channel, marbles)
        ClientIRCPokemon.init(self, username, get_pokemoncg_token, pcg, POKEMON)
        self.log = log
        self.log_file = log_file

    def on_pubmsg(self, client, message):
        ClientIRCMarbles.on_pubmsg(self, client, message)
        ClientIRCPokemon.on_pubmsg(self, client, message)

    def die(self, msg="Bye, cruel world!"):
        ClientIRCPokemon.die(self)
        self.connection.disconnect(msg)
        self.__active = False


class ThreadChat(ThreadChatO):
    def __init__(self, username, token, channel, channel_id, get_pokemoncg_token, marbles, pcg):
        ThreadChatO.__init__(self, username, token, channel)
        self.marbles = marbles
        self.pcg = pcg
        self.channel_id = channel_id
        self.get_pokemoncg_token_func = get_pokemoncg_token

    def get_pokemoncg_token(self):
        return self.get_pokemoncg_token_func(self.channel_id)

    def run(self):
        self.chat_irc = ClientIRC(
            self.username,
            self.token,
            self.channel,
            self.get_pokemoncg_token,
            self.marbles,
            self.pcg
        )
        log(text=f"Join IRC Chat: {self.channel}")
        POKEMON.channel_online(self.channel)
        self.chat_irc.start()

    def stop(self):
        ThreadChatO.stop(self)
        leave_channel(self.channel)

ChatPresence = ChatPresenceO
