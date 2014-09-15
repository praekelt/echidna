import os
import datetime
import threading
import types
import json
from time import sleep
from subprocess import Popen, PIPE, STDOUT

import requests

from ws4py.client.threadedclient import WebSocketClient


NOW_TIMESTAMP = 1410437764424


def object_to_lists(obj):
    """Convert obj into nested lists. Useful when comparing nested
    dictionaries."""

    li = []

    if isinstance(obj, types.DictType):
        keys = obj.keys()
        keys.sort()
        for k in keys:
            v = obj[k]
            if isinstance(v, types.DictType):
                li.append(object_to_lists(v))
            elif isinstance(v, (types.ListType, types.TupleType)):
                for el in v:
                    li.append(object_to_lists(el))
            else:
                li.append((k, v))

    elif isinstance(obj, (types.ListType, types.TupleType)):
        for el in obj:
            li.append(object_to_lists(el))

    else:
        return obj

    return li


class Client(WebSocketClient):

    def __init__(self, name):
        self.name = name
        self._messages = []
        super(Client, self).__init__("ws://127.0.0.1:8888/subscribe")
        self.connect()

    def received_message(self, message):
        print "%s received message %s" % (self.name, message.data)
        self._messages.insert(0, json.loads(message.data))

    @property
    def message_count(self):
        return len(self._messages)

    def has_message(self, di):
        to_check = object_to_lists(di)
        for i in range(1, 10):
            for message in self._messages:
                tu = object_to_lists(message)
                if tu == to_check:
                    return True
            sleep(0.1)
        return False


class ClientThread(threading.Thread):
    """Used to wrap Client so it doesn't block the main thread"""

    def __init__(self, name):
        super(ClientThread, self).__init__()
        self._socket = Client(name)

    def run(self):
        self._socket.run_forever()

    @property
    def socket(self):
        return self._socket


def doit():
    # Create clients
    client1 = ClientThread("client1")
    client1.start()
    client2 = ClientThread("client2")
    client2.start()
    client3 = ClientThread("client3")
    client3.start()

    # Client1 opens the app before any cards are published
    di = {
        "msg_type": "subscribe",
        "channel": "news",
    }
    client1.socket.send(json.dumps(di))
    di = {
        "msg_type": "subscribe",
        "channel": "sport",
    }
    client1.socket.send(json.dumps(di))
    sleep(0.5)
    assert client1.socket.message_count == 0, "Client 1 must not have any messages"

    # Create initial cards
    channels = {}
    for channel in ("news", "news", "sport", "sport"):
        channels.setdefault(channel, 0)
        idx = channels[channel]
        data = {"text": "message %s" % idx, "created": NOW_TIMESTAMP + idx * 60}
        channels[channel] = channels[channel] + 1
        r = requests.post(
            "http://127.0.0.1:8888/publish/%s/" % channel,
            data=json.dumps(data)
        )
        assert r.content == """{"success": true}"""

    # Client2 opens the app and receives first cards 1-4
    for channel in ("news", "sport"):
        di = {
            "msg_type": "subscribe",
            "channel": channel,
        }
        client2.socket.send(json.dumps(di))
    sleep(0.5)
    channels = {}
    for channel in ("news", "news", "sport", "sport"):
        channels.setdefault(channel, 0)
        idx = channels[channel]
        di = {
            "card": {"text": "message %s" % idx, "created": NOW_TIMESTAMP + idx * 60},
            "channel": channel,
            "msg_type": "card"
        }
        assert client2.socket.has_message(di), "Client 2: card not received: %s" % repr(di)
        channels[channel] = channels[channel] + 1

    # Client 3 re-opens the app at NOW_TIMESTAMP + 30 and receives cards 3 and 4
    for channel in ("news", "sport"):
        di = {
            "msg_type": "subscribe",
            "channel": channel,
            "last_seen": NOW_TIMESTAMP + 30
        }
        client3.socket.send(json.dumps(di))
    sleep(0.5)
    channels = {}
    for channel in ("news", "news", "sport", "sport"):
        channels.setdefault(channel, 0)
        idx = channels[channel]
        di = {
            "card": {"text": "message %s" % idx, "created": NOW_TIMESTAMP + idx * 60},
            "channel": channel,
            "msg_type": "card"
        }
        if idx == 0:
            # Client may not receive cards 1 and 2
            assert not client3.socket.has_message(di), "Client 3: card received: %s" % repr(di)
        else:
            # Client must receive cards 3 and 4
            assert client3.socket.has_message(di), "Client 3: card not received: %s" % repr(di)
        channels[channel] = channels[channel] + 1

    # Publish one more card per channel
    channels = {}
    for channel in ("news", "sport"):
        channels.setdefault(channel, 2)
        idx = channels[channel]
        data = {"text": "message %s" % idx, "created": NOW_TIMESTAMP + idx * 60}
        channels[channel] = channels[channel] + 1
        r = requests.post(
            "http://127.0.0.1:8888/publish/%s/" % channel,
            data=json.dumps(data)
        )
        assert r.content == """{"success": true}"""
    sleep(0.5)

    # All clients receive cards 5 and 6
    for n, client in enumerate((client1, client2, client3)):
        channels = {}
        for channel in ("news", "sport"):
            channels.setdefault(channel, 2)
            idx = channels[channel]
            di = {
                "card": {"text": "message %s" % idx, "created": NOW_TIMESTAMP + idx * 60},
                "channel": channel,
                "msg_type": "card"
            }
            assert client.socket.has_message(di), "Client %s: card not received: %s" % (n+1, repr(di))
            channels[channel] = channels[channel] + 1

    # Close clients
    client1.socket.close()
    client1.join()
    client2.socket.close()
    client2.join()
    client3.socket.close()
    client3.join()


if __name__ == "__main__":
    process = Popen(
        [
            './ve/bin/twistd',
            '--pidfile=/tmp/echidna.pid',
            '--logfile=/tmp/echidna.log',
            'cyclone',
            '--app=echidna.demo.server.DemoServer',
            '--port=8888'
        ],
        stdout=PIPE,
        stderr=PIPE,
        bufsize=1
    )
    try:
        # Give it time to start up
        sleep(3)

        doit()
    finally:
        os.system("kill `cat /tmp/echidna.pid`")
