from zope.interface import implements

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from twisted.application import internet

from loom.scheduler import LoomSchedulingService

class Options(usage.Options):
    optParameters = [
        ["config", "c", "~/.loom.yaml,/etc/loom.yaml,/etc/loom/loom.yaml", "comma seperated list of possible loom configurations"]]

class LoomSchedulingServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "loom"
    description = "Concurrent task-scheduling for clusters."
    options = Options

    def makeService(self, options):
        "Construct a LoomSchedulingService"
        return LoomSchedulingService(options['config'])


service_maker = LoomSchedulingServiceMaker()







