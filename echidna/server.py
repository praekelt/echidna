"""hedley marker"""
import json
import datetime

from twisted.web.resource import Resource
from twisted.web import server
from twisted.internet import defer, reactor
from twisted.python import log

from autobahn.twisted.websocket import (WebSocketServerFactory,
                                        WebSocketServerProtocol)
from autobahn.twisted.resource import WebSocketResource

from echidna.cards.base import CardStore


class EchidnaResource(Resource):

    def __init__(self, debug=False, **config):
        Resource.__init__(self)

        channel_class = config.pop("channel_class", None)
        self.store = CardStore(channel_class, **config) if channel_class \
            else CardStore(**config)

        host = config.get("host", "localhost")
        port = config.get("port", 8888)
        factory = WebSocketServerFactory(
            "ws://%s:%s" % (host, port), debug=debug, debugCodePaths=debug
        )
        factory.store = self.store
        factory.protocol = SubscriptionProtocol
        ws_resource = WebSocketResource(factory)

        self.putChild("publish", PublicationResource(self.store))
        self.putChild("subscribe", ws_resource)
        self.putChild("totals", TotalsResource(self.store))


class PublicationResource(Resource):

    def __init__(self, store):
        Resource.__init__(self)
        self.store = store

    def getChild(self, name, request):
        return PublicationChannelResource(self.store, name)


class PublicationChannelResource(Resource):

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

        return json.dumps({"success": True})


class TotalsResource(Resource):

    def __init__(self, store):
        Resource.__init__(self)
        self.store = store

    def getChild(self, name, request):
        return TotalsChannelResource(self.store, name)


class TotalsChannelResource(Resource):

    def __init__(self, store, channel):
        Resource.__init__(self)
        self.store = store
        self.channel = channel

    def render_GET(self, request):
        request.responseHeaders.addRawHeader(b"content-type",
                                             b"application/json")
        # get the last 24 hour-based buckets
        res = {
            "totals": self.store.totals(self.channel)
        }
        return json.dumps(res)


class SubscriptionProtocol(WebSocketServerProtocol):

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
        for card in cards:
            self.on_publish(channel_name, card)

    def handle_subscribe(self, msg):
        channel_name = msg.get("channel")
        last_seen = msg.get("last_seen", None)
        client_id = msg.get("id", "Anon")
        if last_seen is None:
            last_seen = int(datetime.datetime.utcnow().strftime("%s")) - 10800
        if not isinstance(channel_name, unicode):
            return

        self.client.given_id = client_id
        d = self.factory.store.subscribe(channel_name, self.client, last_seen)
        return d.addCallback(
            lambda cards: self.send_cards(channel_name, cards))

    def handle_unsubscribed(self, msg):
        channel_name = msg.get("channel")
        if not isinstance(channel_name, unicode):
            return
        d = self.factory.store.unsubscribe(channel_name, self.client)
        return d

    def handle_ping(self, msg):
        self.sendMessage("1", False)

    def handle_invalid(self, msg):
        self.send_error("invalid message", original_message=msg)


class EchidnaSite(server.Site):

    resourceClass = EchidnaResource

    def __init__(self, resource, *args, **kwargs):
        self.config = kwargs.pop('config', {})
        server.Site.__init__(self, resource, *args, **kwargs)

    def startFactory(self):
        server.Site.startFactory(self)
        d = defer.DeferredList([])
        d.addCallback(self.setup_resource)
        d.addErrback(self.shutdown)
        return d

    def shutdown(self, failure):
        log.err(failure.value)
        reactor.stop()

    def setup_resource(self, results):
        self.resource = self.resourceClass(**self.config)
