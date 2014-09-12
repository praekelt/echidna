# Use ws4py

import datetime
import threading
import json
import types
from time import sleep

import requests

from ws4py.client.threadedclient import WebSocketClient
from ws4py.client.threadedclient import WebSocketBaseClient

from twisted.internet.defer import inlineCallbacks
from twisted.trial.unittest import TestCase
from twisted.internet import reactor
from twisted.internet import defer, protocol

from echidna.server import EchidnaServer
from echidna.cards.interfaces import IClient, ICardStore
from echidna.cards.base import Client, CardStore
from echidna.cards.tests.utils import mk_client, Recorder
from echidna.demo.server import DemoServer


NOW_TIMESTAMP = 1410437764424
server = None
subscriber_thread = None


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


class TestClient(WebSocketClient):

    def __init__(self):
        self._messages = []
        super(TestClient, self).__init__("ws://127.0.0.1:8888/subscribe")
        print "TestClient.__init__ before connect"
        self.connect()
        print "TestClient.__init__ after connect"

    def received_message(self, message):
        print "RECEIVED MESSAGE %s" % message.data
        self._messages.insert(0, json.loads(message.data))

    def has_message(self, di):
        to_check = object_to_lists(di)
        for i in range(1, 10):
            for message in self._messages:
                tu = object_to_lists(message)
                if tu == to_check:
                    return True
            sleep(0.1)
        return False


class SubscriberThread(threading.Thread):
    """Used to wrap TestClient so it doesn't block the main thread"""

    def __init__(self):
        super(SubscriberThread, self).__init__()
        print  "SubscriberThread.__init__ start"
        self._socket = TestClient()
        print  "SubscriberThread.__init__ end"

    def run(self):
        print  "SubscriberThread.run start"
        self._socket.run_forever()
        print  "SubscriberThread.run end"

    @property
    def socket(self):
        return self._socket


class TestApp(TestCase):
    """Simulate clients interacting with the server"""

    subscriber_thread = None

    def setUp(self):
        global server
        if server is None:
            server = reactor.listenTCP(8888, EchidnaServer(root=None), interface="127.0.0.1")
            sleep(1)

        global subscriber_thread
        if subscriber_thread is None:
            subscriber_thread = SubscriberThread()
            subscriber_thread.start()
            sleep(1)


    def test_a_publish_first_cards(self):
        data = {"text": "message 1", "created": NOW_TIMESTAMP}
        r = requests.post(
            "http://127.0.0.1:8888/publish/radio_ga_ga/",
            data=json.dumps(data)
        )
        self.assertEqual(r.content, """{"success": true}""")

    def test_d_initial_connect(self):
        di = {
            "msg_type": "subscribe",
            "channel": "radio_ga_ga",
            "last_seen": int(datetime.datetime.now().strftime("%s"))
        }
        global subscriber_thread
        subscriber_thread.socket.send(json.dumps(di))
        self.assertTrue(subscriber_thread.socket.has_message(
            {"card": {"text": "message 1", "created": NOW_TIMESTAMP}, "channel": "radio_ga_ga", "msg_type": "card"}
        ))

    def test_y_shutdown(self):
        global subscriber_thread
        if subscriber_thread is not None:
            subscriber_thread.socket.close()
            subscriber_thread.join()
            sleep(1)

    @inlineCallbacks
    def test_z_shutdown(self):
        global server
        if server is not None:
            yield server.stopListening()
            server.loseConnection()
