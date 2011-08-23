import os

from twisted.application import service
from twisted.internet import protocol, defer

from ampoule import child, pool

from loom import nodes, jobs, util, amp
from loom.manifest import ManifestWatcher

default_config_paths = [
    '~/.loom.yaml',
    '/etc/loom.yaml',
    '/etc/loom/loom.yaml',
]
  
class LoomSchedulingService(service.Service):
    def __init__(self, config_paths=''):
        self.config_paths = config_paths.split(',')
        self.pp = pool.ProcessPool(amp.JobProtocol, min=1, max=50)
        self.watcher = ManifestWatcher(self.watcherCallback)
        self.jobs = dict()
        self.loadConfigs()

    def stopAllJobs(self):
        "cancel all registered jobs"
        for name, job in self.jobs.items():
            job.stop()

    def startAllJobs(self):
        "start all registered jobs"
        for name, job in self.jobs.items():
            job.start()

    def watcherCallback(self):
        self.stopAllJobs()
        self.loadConfigs()
        self.startAllJobs()

    def loadConfigs(self):
        "load all configs"
        self.config = self.loadBaseConf()
        self.nodes = self.loadNodeConf()
        self.jobs = self.loadJobConfs()
        print self.jobs

    def loadBaseConf(self):
        "load base configuration"
        config_paths = self.config_paths
        if not config_paths:
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

    @defer.inlineCallbacks
    def startService(self):
        "start all loaded jobs"
        yield self.pp.start()
        self.startAllJobs()

    @defer.inlineCallbacks
    def stopService(self):
        "stop all loaded jobs"
        yield self.pp.stop()
        self.stopAllJobs()




