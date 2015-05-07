import uuid
import json
import datetime

from zope.interface import implements
from twisted.internet.defer import succeed
from dateutil.relativedelta import relativedelta
import redis

from echidna.cards.interfaces import IInMemoryChannel, IRedisChannel


class InMemoryChannel(object):
    """
    A channel in an :class:`InCardStore`.
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
                if card['publish_on'] > int(client.last_seen):
                    last_seen_cards.append(card)
            return last_seen_cards

        return self._cards

    def publish(self, card):
        self._cards.append(card)
        for client in self._clients.itervalues():
            client.publish(self.name, card)

    def totals(self):
        return None


class RedisChannel(InMemoryChannel):
    """
    A channel in an :class:`InCardStore`.
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

    def subscribe(self, client, last_seen=None):
        super(RedisChannel, self).subscribe(client, last_seen)
        # record uuid in redis
        now = datetime.datetime.now()
        bucket = "%s-%s" % (self.name, now.strftime("%Y%m%d%H"))
        client_id = getattr(client, "given_id", "Anon")
        if client_id != "Anon":
            self._redis.sadd(bucket, client_id)

    def publish(self, card):
        self._redis.rpush(self._key, json.dumps(card))
        super(RedisChannel, self).publish(card)

    def totals(self):
        now = datetime.datetime.now()
        totals = {}
        for h in range(0, 24):
            dt = now - relativedelta(hours=h)
            bucket = "%s-%s" % (self.name, dt.strftime("%Y%m%d%H"))
            bucket_name = bucket.split('-')[1]
            totals[bucket_name] = self._redis.scard(bucket)

        return totals
