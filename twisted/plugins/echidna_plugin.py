import os

import yaml

from zope.interface import implements

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from twisted.application import internet

from echidna.server import EchidnaSite


class Options(usage.Options):
    optParameters = [
        ["config", "c", "config.yaml", "The handlers config file"],
    ]


class BouncerServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "echidna"
    description = "Echidna"
    options = Options

    def makeService(self, options):
        config_file = options['config']
        config = {}
        if os.path.exists(config_file):
            with open(config_file, 'r') as fp:
                config = yaml.safe_load(fp)

        port = config.pop('port', 8888)

        return internet.TCPServer(int(port),
            EchidnaSite(config))

serviceMaker = BouncerServiceMaker()
