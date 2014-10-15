"""
Echidna demo server.
"""

import os

from cyclone.web import RequestHandler

from echidna.server import EchidnaServer


class DemoServer(EchidnaServer):
    """
    A server to demo Echidna.
    """

    def __init__(self, yaml_file=None, **settings):
        defaults = {
            "template_path": (
                os.path.join(os.path.dirname(__file__), "templates")),
            "static_path": (
                os.path.join(os.path.dirname(__file__), "static")),
            "static_url_prefix": "/static/",
            "autoescape": None,
        }
        defaults.update(settings)
        EchidnaServer.__init__(self, DemoPageHandler, yaml_file, **defaults)


class DemoPageHandler(RequestHandler):
    """
    Render the demo page.
    """

    def get(self):
        self.render("demo.html",
                    api_server="localhost:8888",
                    channels=[
                        ("Visual Radio", "visualradio"),
                        ("radio_ga_ga", "Radio Ga Ga"),
                        ("channel_x", "Channel X"),
                        ("major_tom", "Major Tom"),
                    ])
