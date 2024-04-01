from . import Discord

class MockDiscordAPI():
    def __init__(self):
        self.reset()

    def reset(self):
        self.gets = 0
        self.posts = 0
        self.deletes = 0
        self.requests = []

    def post(self, url, content, file=None):
        self.posts +=1
        self.requests.append(("post", url, content, file))

    def get(self, url):
        self.gets +=1
        self.requests.append(("get", url))

    def delete(self, url):
        self.deletes +=1
        self.requests.append(("delete", url))


class MockDiscord(Discord):
    def connect(self):
        if self.data["auth"] is None:
            return

        self.api = MockDiscordAPI()
        self.connected = True


def create_mock_discord():
    discord = MockDiscord()
    discord.set({
        "auth": "fakeuser",
        "user": "fakeuser"
    })
    discord.connect()
    return discord


def test_discord():
    discord = MockDiscord()
    url = None
    file = None
    data = None
    auth_data = {
        "auth": "fakeuser",
        "user": "fakeuser"
    }

    assert discord.connected is False
    assert discord.api is None
    discord.connect()
    assert discord.connected is False
    assert discord.api is None
    discord.get(url)
    assert discord.api is None
    discord.post(url, data)
    assert discord.api is None
    discord.delete(url)
    assert discord.api is None
    discord.set({})
    discord.connect()
    assert discord.connected is False
    assert discord.api is None
    discord.set(auth_data)
    assert discord.connected is False
    assert discord.api is None
    discord.connect()
    assert discord.connected
    assert discord.api is not None
    assert discord.api.gets == 0
    assert discord.api.posts == 0
    assert discord.api.deletes == 0
    discord.get(url)
    assert discord.api.gets == 1
    assert discord.api.posts == 0
    assert discord.api.deletes == 0
    assert discord.api.requests[-1] == ("get", url)
    discord.post(url, data)
    assert discord.api.gets == 1
    assert discord.api.posts == 1
    assert discord.api.deletes == 0
    assert discord.api.requests[-1] == ("post", url, data, None)
    discord.delete(url)
    assert discord.api.gets == 1
    assert discord.api.posts == 1
    assert discord.api.deletes == 1
    assert discord.api.requests[-1] == ("delete", url)
    discord.api.reset()
    assert discord.api.gets == 0
    assert discord.api.posts == 0
    assert discord.api.deletes == 0
    assert discord.api.requests == []
