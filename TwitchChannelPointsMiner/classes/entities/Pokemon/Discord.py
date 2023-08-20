from ...DiscordAPI import DiscordAPI


class Discord(object):
    def __init__(self):
        self.connected = False
        self.data = {
            "auth": None,
            "user": None,
        }

    def set(self, data):
        for k in data:
            if k in self.data:
                self.data[k] = data[k]

    def connect(self):
        if self.data["auth"] is None:
            return

        self.api = DiscordAPI(self.data["auth"])
        self.connected = True

    def get(self, url):
        if self.connected:
            return self.api.get(url)
        return None

    def delete(self, url):
        if self.connected:
            return self.api.delete(url)
        return None

    def post(self, url, data, file=None):
        if self.connected:
            return self.api.post(url, data, file)

    def get_role(self, role):
        if self.data["roles"] is not None:
            if role in self.data["roles"]:
                return self.data["roles"][role]

        return None
