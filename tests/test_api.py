from . import CGApi

class MockApi(CGApi):
    def __init__(self):
        CGApi.__init__(self, "token")
        self.requests = []
        self.responses = []

    def _do_request(self, method, url, payload={}):
        if len(self.requests) <= len(self.responses):
            self.responses.append({})
        self.requests.append((method, url, payload))
        print(self.requests, self.responses)
        return self.responses[len(self.requests) - 1]


def test_mock_api():
    api = MockApi()
    response = api.get_pokemon(123)
    assert response == {}

    mocked_response = {"data": True}
    api.responses.append(mocked_response)
    response = api.get_pokemon(123)
    assert response == mocked_response

    assert api.requests[0][0] == "GET"