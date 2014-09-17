from echidna.cards.base import Client


class Recorder(object):
    """
    Recording callback for channel clients.
    """

    def __init__(self):
        self.calls = []

    def __call__(self, channel_name, card):
        self.calls.append((channel_name, card))


def mk_client(callback=None):
    if callback is None:
        callback = lambda channel_name, card: None
    return Client(callback)
