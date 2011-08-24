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
        self.watcher = ManifestWatcher(self.watcherCallback)
        self.loadConfigs(config_paths)

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
        self.loadConfigs(self.config_paths)
        self.startAllJobs()

    def loadConfigs(self, config_paths):
        "load all configs"
        self.config_paths = config_paths.split(',')
        self.config = self.loadBaseConf()
        self.pp = self.loadPool()
        self.nodes = self.loadNodeConf()
        self.jobs = self.loadJobConfs()

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

    def loadPool(self):
        "initialize the process pool"
        min = self.config.get('min_workers', 0)
        max = self.config.get('max_workers', 10)
        print "*\n"*5
        print "min,",min
        print "max,",max
        return pool.ProcessPool(amp.JobProtocol, min=0, max=50)
        

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




