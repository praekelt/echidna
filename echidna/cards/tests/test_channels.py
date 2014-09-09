from twisted.internet.defer import inlineCallbacks
from twisted.trial.unittest import TestCase

from echidna.cards.channels import InMemoryChannel
from echidna.cards.tests.utils import mk_client, Recorder


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
