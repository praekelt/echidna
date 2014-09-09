"""
Tools for storing and retrieiving cards in memory.
"""

import uuid
import json

from zope.interface import implements
from zope.dottedname.resolve import resolve
from twisted.internet.defer import succeed
import redis

from echidna.cards.interfaces import IInMemoryChannel, IRedisChannel, \
    IClient, ICardStore


class InMemoryClient(object):
    """
    A simple client object for :class:`InMemoryCardStore`.
    """

    implements(IClient)

    def __init__(self, callback):
        self.client_id = uuid.uuid4().get_hex()
        self.callback = callback
        self.last_seen = None

    def publish(self, channel_name, card):
        self.callback(channel_name, card)


class InMemoryChannel(object):
    """
    A channel in an :class:`InMemoryCardStore`.
    """

    implements(IInMemoryChannel)

    def __init__(self, name):
        self.name = name
        self._clients = {}
        self._cards = []

    def subscribe(self, client, last_seen=None):
        client.last_seen = last_seen
        self._clients[client.client_id] = client

    def remove(self, client):
        if client.client_id in self._clients:
            del self._clients[client.client_id]

    def cards(self, client=None):
        if (client is not None) and (client.last_seen is not None):
            last_seen_cards = []
            for card in self._cards:
                if card['created'] > int(client.last_seen):
                    last_seen_cards.append(card)
            return last_seen_cards

        return self._cards

    def publish(self, card):
        self._cards.append(card)
        for client in self._clients.itervalues():
            client.publish(self.name, card)


class RedisChannel(InMemoryChannel):
    """
    A channel in an :class:`InMemoryCardStore`.
    """

    implements(IRedisChannel)

    def __init__(self, name):
        super(RedisChannel, self).__init__(name)
        self._redis = redis.Redis("localhost")
        self._key = "echidna%scards" % self.name
        values = self._redis.lrange(self._key, 0, -1)
        try:
            self._cards = [json.loads(v) for v in values]
        except ValueError:
            pass

    def publish(self, card):
        self._redis.rpush(self._key, json.dumps(card))
        super(RedisChannel, self).publish(card)


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
            # todo: put in config
            #self._channels[name] = resolve(
            #    "echidna.cards.memory_store.RedisChannel")(name)
            self._channels[name] = resolve(
                "echidna.cards.memory_store.InMemoryChannel")(name)

        return self._channels[name]

    def create_client(self, callback):
        client = InMemoryClient(callback)
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
