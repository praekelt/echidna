import uuid
import json
import importlib

from zope.interface import implements
from twisted.internet.defer import succeed

from echidna.cards.interfaces import IClient, ICardStore


class Client(object):
    """
    A simple client object for :class:`InCardStore`.
    """

    implements(IClient)

    def __init__(self, callback):
        self.client_id = uuid.uuid4().get_hex()
        self.callback = callback
        self.last_seen = None

    def publish(self, channel_name, card):
        self.callback(channel_name, card)


class CardStore(object):
    """
    Stores cards in memory.

    .. note::

       Not for use in environments which need to run multiple Echidna
       servers. Really?
    """

    implements(ICardStore)

    def __init__(
        self,
        channel_class="echidna.cards.channels.InMemoryChannel"
    ):
        self._channels = {}
        self._channel_class = channel_class

    def _ensure_channel(self, name):
        if name not in self._channels:
            li = self._channel_class.split('.')
            module = importlib.import_module('.'.join(li[:-1]))
            self._channels[name] = getattr(module, li[-1])(name)
        return self._channels[name]

    def create_client(self, callback):
        client = Client(callback)
        return succeed(client)

    def remove_client(self, client):
        for channel in self._channels.itervalues():
            channel.remove(client)
        return succeed(None)

    def subscribe(self, channel_name, client, last_seen=None):
        channel = self._ensure_channel(channel_name)
        channel.subscribe(client, last_seen)
        return succeed(channel.cards(client))

    def unsubscribe(self, channel_name, client):
        channel = self._ensure_channel(channel_name)
        channel.remove(client)
        return succeed(None)

    def publish(self, channel_name, card):
        channel = self._ensure_channel(channel_name)
        channel.publish(card)
        return succeed(None)

    def totals(self, channel_name):
        channel = self._ensure_channel(channel_name)
        return channel.totals()
