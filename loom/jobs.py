import sys, os

from twisted.internet import defer, task, reactor
from twisted.internet.protocol import Factory
from twisted.internet.utils import getProcessOutputAndValue
from twisted.protocols import amp

from twisted.scheduling.cron import CronSchedule
from twisted.scheduling.task import ScheduledCall

from ampoule import child, pool

from fabric.api import run, env

from loom import amp

def load(scheduler, jobs_path, data_path=None):
    "load all jobs from specified yaml file"
    # load yaml front-matter data
    front_matter = ''
    if data_path:
        with open(data_path, 'r') as yaml:
            front_matter = amp.load(yaml) + "\n\n"
    # find all job files under jobs path
    job_files = []
    for r,d,f in os.walk(jobs_path):
        for files in f:
            if files.endswith(".yaml"):
                job_files.append(os.path.join(r,files))
    # load each job file found
    jobs = {}
    for job_file in job_files:
        with open(job_file, 'r') as yaml:
            data = amp.load(front_matter + yaml.read())
        if 'jobs' in data:
            for name, job in data['jobs'].items():
                jobs[name] = LoomJob(scheduler, name, **job)
    print len(jobs), "jobs loaded."
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
