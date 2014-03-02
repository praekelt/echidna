from cyclone.web import Application, RequestHandler
from cyclone.websocket import WebSocketHandler


class EchidnaServer(Application):
    def __init__(self, **settings):
        handlers = [
            (r"/", RootHandler),
            (r"/publish", PublicationHandler),
            (r"/subscribe", SubscriptionHandler),
        ]
        Application.__init__(self, handlers, **settings)


class RootHandler(RequestHandler):
    def get(self):
        self.render("demo.html")


class PublicationHandler(RequestHandler):
    def post(self):
        pass


class SubscriptionHandler(WebSocketHandler):
    def connectionMade(self, *args, **kw):
        pass

    def connectionLost(self, reason):
        pass

    def messageReceived(self, msg):
        self.sendMessage("foo")
