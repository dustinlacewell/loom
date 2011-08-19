from twisted.application import internet, service
from loom.scheduler import LoomSchedulingService

application = service.Application("loomd")
LoomSchedulingService().setServiceParent(application)