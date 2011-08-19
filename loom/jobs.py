import sys

from twisted.internet import defer, task, reactor
from twisted.internet.protocol import Factory
from twisted.internet.utils import getProcessOutputAndValue
from twisted.protocols import amp

from twisted.scheduling.cron import CronSchedule
from twisted.scheduling.task import ScheduledCall

from ampoule import child, pool

from fabric.api import run, env

from loom import amp

def load(scheduler, filename):
    "load all jobs from specified yaml file"
    jobs = {}
    with open(filename, 'r') as yaml:
        data = amp.load(yaml)
    if 'jobs' in data:
        for name, job in data['jobs'].items():
            jobs[name] = LoomJob(scheduler, name, **job)
        return jobs

class LoomJob(object):
    "represents a scheduled job"
    def __init__(self, scheduler, name, **kwargs):
        self.scheduler = scheduler
        self.name = name
        self.taskpath = kwargs['task']
        self.args = amp.dump(kwargs.get('args', []))
        self.kwargs = amp.dump(kwargs.get('kwargs', {}))
        self.targets = [scheduler.nodes[host] for host in kwargs['targets']]
        self.schedule = CronSchedule(kwargs.get('schedule', "* * * * *"))
        self._timer = ScheduledCall(self.execute)
        self.description = kwargs.get(
            'description', "{task} @ {targets}".format(
                task=self.taskpath,
                targets=str(self.targets)))

    def start(self):
        "enable schedule for this job"
        self._timer.start(self.schedule)
        self.execute()

    def stop(self):
        "disable schedule for this job"
        self._timer.stop()

    @defer.inlineCallbacks
    def execute(self):
        "execute scheduled task"
        deferreds = []
        pp = pool.ProcessPool(amp.JobProtocol, min=1, max=5)
        yield pp.start()
        for node in self.targets:
            deferreds.append(pp.doWork(amp.ExecuteTask, **{
                        'nodeinfo': node.__amp__(),
                        'taskpath': self.taskpath,
                        'args': self.args,
                        'kwargs': self.kwargs}))
        results = yield defer.gatherResults(deferreds)
        yield pp.stop()
