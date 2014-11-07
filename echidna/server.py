import json

import yaml

from twisted.web.resource import Resource
from autobahn.twisted.websocket import (WebSocketServerFactory,
                                        WebSocketServerProtocol)
from autobahn.twisted.resource import WebSocketResource

from echidna.cards.base import CardStore


class EchidnaServer(Resource):
    def __init__(self, base_url, debug=False, yaml_file=None, **settings):
        Resource.__init__(self)

        # Parse YAML config if supplied
        kw = {}
        if yaml_file is not None:
            try:
                fp = open(yaml_file, "r")
            except IOError:
                pass
            else:
                try:
                    config = yaml.load(fp)
                    kw.update(config)
                except yaml.scanner.ScannerError:
                    pass
                finally:
                    fp.close()

        self.store = CardStore(**kw)

        factory = WebSocketServerFactory("ws://" + base_url, debug=debug,
                                         debugCodePaths=debug)
        factory.store = self.store
        factory.protocol = SubscriptionHandlerProtocol
        ws_resource = WebSocketResource(factory)

        self.putChild("publish", PublicationHandler(self.store))
        self.putChild("subscribe", ws_resource)


class PublicationHandler(Resource):
    def __init__(self, store):
        Resource.__init__(self)
        self.store = store

    def getChild(self, name, request):
        return PublicationChannelHandler(self.store, name)


class PublicationChannelHandler(Resource):
    def __init__(self, store, channel):
        Resource.__init__(self)
        self.store = store
        self.channel = channel

    def render_POST(self, request):
        print 'Got card for channel: [%s]' % self.channel
        request.responseHeaders.addRawHeader(b"content-type",
                                             b"application/json")
        try:
            card = json.loads(request.content.read())
        except:
            request.setResponseCode(400)
            return json.dumps("Invalid card in request body.")
        self.store.publish(self.channel, card)
        print 'saved card'

        return json.dumps({"success": True})


class SubscriptionHandlerProtocol(WebSocketServerProtocol):
    def __init__(self):
        # WebSocketServerProtocol.__init__(self)
        self.client = None

    def _set_client(self, client):
        self.client = client

    def onConnect(self, *args, **kw):
        d = self.factory.store.create_client(self.on_publish)
        return d.addCallback(self._set_client)

    def onClose(self, wasClea, code, reason):
        if self.client is not None:
            return self.factory.store.remove_client(self.client)

    def onMessage(self, payload, isBinary):
        print "Received message: %s" % str(payload)
        try:
            msg = json.loads(payload)
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
        print "Send card %s" % repr(msg)
        self.sendMessage(json.dumps(msg), False)

    def send_error(self, reason, **data):
        msg = {
            "msg_type": "error",
            "reason": reason,
        }
        msg.update(data)
        self.sendMessage(json.dumps(msg), False)

    def send_cards(self, channel_name, cards):
        print "Send cards for channel %s" % channel_name
        print len(cards)
        for card in cards:
            self.on_publish(channel_name, card)

    def handle_subscribe(self, msg):
        channel_name = msg.get("channel")
        last_seen = msg.get("last_seen", None)
        if not isinstance(channel_name, unicode):
            return

        d = self.factory.store.subscribe(channel_name, self.client, last_seen)
        return d.addCallback(
            lambda cards: self.send_cards(channel_name, cards))

    def handle_unsubscribed(self, msg):
        channel_name = msg.get("channel")
        if not isinstance(channel_name, unicode):
            return
        d = self.factory.store.unsubscribe(channel_name, self.client)
        return d

    def handle_invalid(self, msg):
        self.send_error("invalid message", original_message=msg)
