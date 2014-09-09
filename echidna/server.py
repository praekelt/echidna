import json

from cyclone.web import Application, RequestHandler, HTTPError
from cyclone.websocket import WebSocketHandler

from echidna.cards.base import CardStore


class EchidnaServer(Application):
    def __init__(self, root, yaml_file, **settings):
        # todo: get channel_class from settings and pass to constructor
        #import pdb;pdb.set_trace()
        # if bla in yaml pass arg to cardstore
        self.store = CardStore()
        handlers = [
            (r"/", root),
            (r"/publish/(?P<channel>.*)/", PublicationHandler,
             dict(store=self.store)),
            (r"/subscribe", SubscriptionHandler,
             dict(store=self.store)),
        ]
        Application.__init__(self, handlers, **settings)


class PublicationHandler(RequestHandler):
    def initialize(self, store):
        self.store = store

    def post(self, channel):
        try:
            channel = self.decode_argument(channel, "channel")
        except:
            raise HTTPError(400, "Invalid value for channel.")
        try:
            card = json.loads(self.request.body)
        except:
            raise HTTPError(400, "Invalid card in request body.")
        self.store.publish(channel, card)
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps({"success": True}))


class SubscriptionHandler(WebSocketHandler):
    def initialize(self, store):
        self.store = store
        self.client = None

    def _set_client(self, client):
        self.client = client

    def connectionMade(self, *args, **kw):
        d = self.store.create_client(self.on_publish)
        return d.addCallback(self._set_client)

    def connectionLost(self, reason):
        if self.client is not None:
            return self.store.remove_client(self.client)

    def messageReceived(self, msg):
        try:
            msg = json.loads(msg)
        except:
            return
        if not isinstance(msg, dict):
            return
        msg_type = msg.get("msg_type", "invalid")
        if not isinstance(msg_type, unicode):
            return
        handler = getattr(self, "handle_" + msg_type, self.handle_invalid)
        handler(msg)

    def on_publish(self, channel_name, card):
        return self.send_card(channel_name, card)

    def send_card(self, channel_name, card):
        msg = {
            "msg_type": "card",
            "channel": channel_name,
            "card": card,
        }
        self.sendMessage(json.dumps(msg))

    def send_error(self, reason, **data):
        msg = {
            "msg_type": "error",
            "reason": reason,
        }
        msg.update(data)
        self.sendMessage(json.dumps(msg))

    def send_cards(self, channel_name, cards):
        for card in cards:
            self.on_publish(channel_name, card)

    def handle_subscribe(self, msg):
        channel_name = msg.get("channel")
        last_seen = msg.get("last_seen", None)
        if not isinstance(channel_name, unicode):
            return

        d = self.store.subscribe(channel_name, self.client, last_seen)
        return d.addCallback(
            lambda cards: self.send_cards(channel_name, cards))

    def handle_unsubscribed(self, msg):
        channel_name = msg.get("channel")
        if not isinstance(channel_name, unicode):
            return
        d = self.store.unsubscribe(channel_name, self.client)
        return d

    def handle_invalid(self, msg):
        self.send_error("invalid message", original_message=msg)
