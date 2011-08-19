from twisted.application import service
from twisted.internet import protocol

from loom import nodes, jobs

class LoomSchedulingService(service.Service):
  def __init__(self):
      self.nodes = nodes.load('nodes.yaml')
      self.jobs = jobs.load(self, 'jobs/example.yaml')

  def startService(self):
      for name, job in self.jobs.items():
          job.start()

  def stopService(self):
      for name, job in self.jobs.items():
          job.stop()





