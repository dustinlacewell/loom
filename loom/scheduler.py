import os

from twisted.application import service
from twisted.internet import protocol

from loom import nodes, jobs, amp

default_config_paths = [
    '~/.loom.yaml',
    '/etc/loom.yaml',
    '/etc/loom/loom.yaml',
]
  
class LoomSchedulingService(service.Service):
    def __init__(self, config_paths=''):
        self.config = self.loadConfiguration(config_paths)
        self.nodes = nodes.load(self.config['nodesfile'])
        self.jobs = jobs.load(self, self.config['jobspath'], self.config.get('datafile'))

    def loadConfiguration(self, config_paths=''):
        config_paths = config_paths.split(',')
        if not config_paths:
            config_paths = default_config_paths
        for path in config_paths:
            if os.path.isfile(path):
                return amp.load(open(path, 'r'))
        raise Exception('No configuration could be found!')

    def startService(self):
        for name, job in self.jobs.items():
            job.start()

    def stopService(self):
        for name, job in self.jobs.items():
            job.stop()





