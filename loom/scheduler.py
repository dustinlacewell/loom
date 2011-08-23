import os

from twisted.application import service
from twisted.internet import protocol

from loom import nodes, jobs, util
from loom.manifest import ManifestWatcher

default_config_paths = [
    '~/.loom.yaml',
    '/etc/loom.yaml',
    '/etc/loom/loom.yaml',
]
  
class LoomSchedulingService(service.Service):
    def __init__(self, config_paths=''):
        self.config_paths = config_paths.split(',')
        self.watcher = ManifestWatcher(self.loadConfigs)
        self.jobs = dict()
        self.loadConfigs()

    def cancelAllJobs(self):
        "cancel all registered jobs"
        for name, job in self.jobs.items():
            job.stop()

    def loadConfigs(self):
        "load all configs"
        self.config = self.loadBaseConf()
        self.nodes = self.loadNodeConf()
        self.jobs = self.loadJobConfs()

    def loadBaseConf(self):
        "load base configuration"
        if not self.config_paths:
            config_paths = default_config_paths
        for path in config_paths:
            if os.path.isfile(path):
                self.watcher.watch(path)
                return util.load(open(path, 'r'))
        raise Exception('No configuration could be found!')

    def loadNodeConf(self):
        "load node manifest"
        nodefile = self.config['nodesfile']
        self.watcher.watch(nodefile)
        return nodes.load(nodefile)

    def loadJobConfs(self):
        "load all job manifests"
        return jobs.load(self, 
                         self.config['jobspath'], 
                         self.config.get('datafile'))

    def startService(self):
        "start all loaded jobs"
        for name, job in self.jobs.items():
            job.start()

    def stopService(self):
        "stop all loaded jobs"
        self.cancelAllJobs()




