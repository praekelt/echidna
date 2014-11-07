"""
Echidna demo server.
"""

# import os
import sys

from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
# from twisted.web.static import File

from echidna.server import EchidnaServer


if __name__ == '__main__':

    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        log.startLogging(sys.stdout)
        debug = True
    else:
        debug = False

    root = EchidnaServer('0.0.0.0:8888', debug)
    # root.putChild("static", File(os.path.join(os.path.dirname(__file__), "static")))

    site = Site(root)
    reactor.listenTCP(8888, site)
    print 'starting reactor run'
    reactor.run()
