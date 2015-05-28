import json

import pika
from pika.adapters import twisted_connection
from twisted.application import service
from twisted.internet import defer, reactor, protocol
from treq import post


class MonitorService(service.Service):
    """Receive and pass on messages from a RabbitMQ exchange"""

    def connect(self):
        parameters = pika.ConnectionParameters()
        cc = protocol.ClientCreator(
            reactor, twisted_connection.TwistedProtocolConnection, parameters)
        d = cc.connectTCP("localhost", 5672)
        d.addCallback(lambda protocol: protocol.ready)
        d.addCallback(self.setup_connection)
        return d

    @defer.inlineCallbacks
    def setup_connection(self, connection):
        self.channel = yield connection.channel()
        yield self.channel.exchange_declare(exchange="echidna", type="fanout")
        result = yield self.channel.queue_declare(exclusive=True)
        queue_name = result.method.queue
        yield self.channel.queue_bind(exchange="echidna", queue=queue_name)
        yield self.channel.basic_qos(prefetch_count=1)
        self.queue_object, self.consumer_tag = yield self.channel.basic_consume(
            queue=queue_name, no_ack=False, exclusive=True)

    @defer.inlineCallbacks
    def process_queue(self):
        while True:
            thing = yield self.queue_object.get()
            if thing is None:
                break
            ch, method, properties, body = thing
            if body:
                print body
                try:
                    json.loads(body)
                except ValueError:
                    print "NOT JSON"
                    pass
                else:
                    yield post(
                        "http://localhost:8888/publish/visualradio",
                        body,
                        headers={"Content-Type": ["application/json"]}
                    )
            yield ch.basic_ack(delivery_tag=method.delivery_tag)

    @defer.inlineCallbacks
    def startService(self):
        self.running = 1
        yield self.connect()
        self.process_d = self.process_queue()

    @defer.inlineCallbacks
    def stopService(self):
        if not self.running:
            return
        yield self.channel.basic_cancel(callback=None, consumer_tag=self.consumer_tag)
        self.queue_object.put(None)
        yield self.process_d
        self.running = 0


def makeService():
    return MonitorService()
