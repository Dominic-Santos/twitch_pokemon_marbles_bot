class MockLogger():
    def __init__(self):
        self.reset()

    def reset(self):
        self.called = {}
        self.calls = []

    def log(self, color, msg):
        self.calls.append((color, msg))
        self.called[color] = self.called.get(color, 0) + 1


def test_logger():
    logger = MockLogger()
    log = logger.log

    assert logger.called.get("green", 0) == 0
    assert len(logger.calls) == 0

    to_log = ("green", "greatsuccess!")
    log(*to_log)
    assert logger.called.get("green", 0) == 1
    assert len(logger.calls) == 1
    assert logger.calls[-1] == to_log

    log(*to_log)
    assert logger.called.get("green", 0) == 2
    assert len(logger.calls) == 2
    assert logger.calls[-1] == to_log
