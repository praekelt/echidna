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

    def __init__(self, **settings):
        defaults = {
            "template_path": (
                os.path.join(os.path.dirname(__file__), "templates")),
            "static_path": (
                os.path.join(os.path.dirname(__file__), "static")),
            "static_url_prefix": "/static/",
            "xsrf_cookies": True,
            "autoescape": None,
        }
        defaults.update(settings)
        EchidnaServer.__init__(self, DemoPageHandler, **defaults)


class DemoPageHandler(RequestHandler):
    """
    Render the demo page.
    """

    def get(self):
        self.render("demo.html", api_server="localhost:8888")
