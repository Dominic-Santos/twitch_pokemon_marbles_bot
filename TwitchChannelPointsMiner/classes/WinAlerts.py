import win32api
from threading import Thread


def send_alert(title, msg):
    def alert():
        win32api.MessageBox(0, msg, title, 0x00001000)

    worker = Thread(target=alert)
    worker.setDaemon(True)
    worker.start()
