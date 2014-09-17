from twisted.internet.defer import inlineCallbacks
from twisted.trial.unittest import TestCase

from echidna.cards.interfaces import IClient, ICardStore
from echidna.cards.base import Client, CardStore
from echidna.cards.tests.utils import mk_client, Recorder


class TestClient(TestCase):
    def test_implements_IClient(self):
        client = mk_client()
        self.assertTrue(IClient.providedBy(client))

    def test_has_client_id(self):
        client = mk_client()
        self.assertTrue(isinstance(client.client_id, str))

    def test_publish(self):
        recorder = Recorder()
        client = mk_client(recorder)
        card = object()
        client.publish("radio_ga_ga", card)
        self.assertEqual(recorder.calls, [("radio_ga_ga", card)])


'''
class TestInMemoryChannel(TestCase):
    def test_create(self):
        channel = InMemoryChannel("radio_ga_ga")
        self.assertEqual(channel.name, "radio_ga_ga")

    def assert_clients(self, channel, clients):
        self.assertEqual(
            channel._clients.items(),
            [(client.client_id, client) for client in clients])

    def assert_cards(self, channel, cards):
        self.assertEqual(channel.cards(), cards)

    def test_subscribe(self):
        channel = InMemoryChannel("radio_ga_ga")
        client = mk_client()
        self.assert_clients(channel, [])
        channel.subscribe(client)
        self.assert_clients(channel, [client])

    def test_remove(self):
        channel = InMemoryChannel("radio_ga_ga")
        client = mk_client()
        channel.subscribe(client)
        self.assert_clients(channel, [client])
        channel.remove(client)
        self.assert_clients(channel, [])

    def test_cards(self):
        channel = InMemoryChannel("radio_ga_ga")
        card1, card2 = object(), object()
        self.assert_cards(channel, [])
        channel.publish(card1)
        self.assert_cards(channel, [card1])
        channel.publish(card2)
        self.assert_cards(channel, [card1, card2])

    def test_publish(self):
        channel = InMemoryChannel("radio_ga_ga")
        card1, card2 = object(), object()
        recorder = Recorder()
        client = mk_client(recorder)
        channel.subscribe(client)

        self.assertEqual(recorder.calls, [])
        channel.publish(card1)
        self.assertEqual(recorder.calls, [
            ("radio_ga_ga", card1),
        ])
        channel.publish(card2)
        self.assertEqual(recorder.calls, [
            ("radio_ga_ga", card1),
            ("radio_ga_ga", card2),
        ])
'''

class TestCardStore(TestCase):
    def test_implements_ICardStore(self):
        store = CardStore()
        self.assertTrue(ICardStore.providedBy(store))

    def mk_store_and_client(self):
        store = CardStore()
        callback = lambda channel_name, card: None
        d = store.create_client(callback)
        return d.addCallback(lambda client: (store, client))

    def assert_subscribed_clients(self, store, expected_subscriptions):
        client_key = lambda c: c.client_id
        actual_subscriptions = {}
        for channel_name, channel in store._channels.iteritems():
            clients = channel._clients.values()
            if clients:
                actual_subscriptions[channel_name] = sorted(
                    clients, key=client_key)
        for clients in expected_subscriptions.values():
            clients.sort(key=client_key)

        self.assertEqual(actual_subscriptions, expected_subscriptions)

    @inlineCallbacks
    def test_create_client(self):
        store = CardStore()
        callback = lambda channel_name, card: None
        client = yield store.create_client(callback)
        self.assertTrue(IClient.providedBy(client))
        self.assertTrue(isinstance(client, Client))
        self.assertTrue(isinstance(client.client_id, str))
        self.assertEqual(client.callback, callback)

    @inlineCallbacks
    def test_remove_client(self):
        store, client = yield self.mk_store_and_client()
        yield store.remove_client(client)

    @inlineCallbacks
    def test_remove_subscribed_client(self):
        store, client = yield self.mk_store_and_client()
        yield store.subscribe("flash", client)
        self.assert_subscribed_clients(store, {"flash": [client]})
        yield store.remove_client(client)
        self.assert_subscribed_clients(store, {})

    @inlineCallbacks
    def test_subscribe(self):
        store, client = yield self.mk_store_and_client()
        cards = yield store.subscribe("flash", client)
        self.assert_subscribed_clients(store, {"flash": [client]})
        self.assertEqual(cards, [])

    @inlineCallbacks
    def test_subscribe_with_existing_cards(self):
        store, client = yield self.mk_store_and_client()
        card1, card2 = object(), object()
        yield store.publish("flash", card1)
        cards = yield store.subscribe("ah-ha", client)
        self.assertEqual(cards, [])
        cards = yield store.subscribe("flash", client)
        self.assertEqual(cards, [card1])

    @inlineCallbacks
    def test_unsubscribe(self):
        store, client = yield self.mk_store_and_client()
        yield store.subscribe("flash", client)
        self.assert_subscribed_clients(store, {"flash": [client]})
        yield store.unsubscribe("flash", client)
        self.assert_subscribed_clients(store, {})

    @inlineCallbacks
    def test_unsubscribe_when_no_subscribed(self):
        store, client = yield self.mk_store_and_client()
        self.assert_subscribed_clients(store, {})
        yield store.unsubscribe("flash", client)
        self.assert_subscribed_clients(store, {})

    @inlineCallbacks
    def test_publish(self):
        store = CardStore()
        card1, card2 = object(), object()
        recorder = Recorder()
        client = yield store.create_client(recorder)
        yield store.publish("ah-ha", card1)
        self.assertEqual(recorder.calls, [])
        cards = yield store.subscribe("ah-ha", client)
        self.assertEqual(recorder.calls, [])
        self.assertEqual(cards, [card1])
        yield store.publish("ah-ha", card2)
        self.assertEqual(recorder.calls, [("ah-ha", card2)])
