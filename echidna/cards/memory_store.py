"""
Tools for storing and retrieiving cards in memory.
"""

import uuid

from zope.interface import implements
from twisted.internet.defer import succeed

from echidna.cards.interfaces import IClient, ICardStore


class InMemoryClient(object):
    """
    A simple client object for :class:`InMemoryCardStore`.
    """

    implements(IClient)

    def __init__(self, callback):
        self.client_id = uuid.uuid4().get_hex()
        self.callback = callback

    def publish(self, channel_name, card):
        self.callback(channel_name, card)


class InMemoryChannel(object):
    """
    A channel in an :class:`InMemoryCardStore`.
    """

    def __init__(self, name):
        self.name = name
        self._clients = {}
        self._cards = []

    def subscribe(self, client):
        self._clients[client.client_id] = client

    def remove(self, client):
        if client.client_id in self._clients:
            del self._clients[client.client_id]

    def cards(self):
        return self._cards

    def publish(self, card):
        self._cards.append(card)
        for client in self._clients.itervalues():
            client.publish(self.name, card)


class InMemoryCardStore(object):
    """
    Stores cards in memory.

    .. note::

       Not for use in environments which need to run multiple Echidna
       servers.
    """

    implements(ICardStore)

    def __init__(self):
        self._channels = {}

    def _ensure_channel(self, name):
        if name not in self._channels:
            self._channels[name] = InMemoryChannel(name)
        return self._channels[name]

    def create_client(self, callback):
        client = InMemoryClient(callback)
        return succeed(client)

    def remove_client(self, client):
        for channel in self._channels.itervalues():
            channel.remove(client)
        return succeed(None)

    def subscribe(self, channel_name, client):
        channel = self._ensure_channel(channel_name)
        channel.subscribe(client)
        return succeed(channel.cards())

    def publish(self, channel_name, card):
        channel = self._ensure_channel(channel_name)
        channel.publish(card)
        return succeed(None)
