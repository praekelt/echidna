"""
Interfaces to card stores.
"""

from zope.interface import Interface


class IChannel(Interface):
    pass


class IInMemoryChannel(IChannel):
    pass


class IRedisChannel(IChannel):
    pass


class ICardStore(Interface):
    """
    An interface for publishing and subscribing to channels of cards.
    """

    def create_client(callback):
        """
        Create a new client.

        :type callback: f(channel_name, card)
        :param callback: function to call when cards are published

        :return: A deferred that fires with a new :class:`IClient`.
        """

    def remove_client(client):
        """
        Clean up a client.

        :type client: :class:`IClient`
        :param client: client to remove

        :return: A deferred that fires once clean up is complete.
        """

    def subscribe(channel_name, client):
        """
        Subscribe to a channel.

        :type channel: str
        :param channel: channel to subscribe to.
        :type client: :class:`IClient`
        :param client: client subscribing to the channel.

        :return: A defered that fires with a list of current cards
                 for the channel once the client is subscribed.
        """

    def unsubscribe(channel_name, client):
        """
        Unsubscribe from a channel.

        :type channel: str
        :param channel: channel to unsubscribe from.
        :type client: :class:`IClient`
        :param client: client unsubscribing from the channel.

        :return: A defered that fires once the client is unsubcribed.
        """

    def publish(channel_name, card):
        """
        Publish a message to a channel.

        :type channel: str
        :param channel: channel to publish to.
        :type card: dict
        :param card: card to publish.
        """


class IClient(Interface):
    """
    An interface for ICardStore clients.

    This is currently an opaque object -- the interface is intentionally empty.
    """
