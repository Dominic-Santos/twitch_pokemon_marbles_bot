import requests


class DiscordAPI(object):
    def __init__(self, auth_token=None):
        self.auth_token = auth_token

    def get_headers(self):
        return {"Authorization": self.auth_token}

    def post(self, url, content, file=None):
        if self.auth_token is not None:
            if file is None:
                requests.post(url, headers=self.get_headers(), data={"content": content})
            else:
                requests.post(url, headers=self.get_headers(), data={"content": content}, files={'file': file})

    def get(self, url):
        if self.auth_token is not None:
            r = requests.get(url, headers=self.get_headers())
            data = r.json()
            return data

    def delete(self, url):
        if self.auth_token is not None:
            r = requests.delete(url, headers=self.get_headers())
            return r.status_code == 204  # all went good
