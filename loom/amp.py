import sys, cStringIO

from twisted.protocols import amp

from ampoule import child

from fabric.api import env

import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

def load(data):
    "yaml loading helper function"
    return yaml.load(data, Loader=Loader)

def dump(data):
    "yaml dumping helper function"
    return yaml.dump(data, Dumper=Dumper)

class ExecuteTask(amp.Command):
    "perform configured task"
    arguments = [
        ('nodeinfo', amp.String()),
        ('taskpath', amp.String()),
        ('args', amp.String()),
        ('kwargs', amp.String())]
    response = [('output', amp.String())]

class JobProtocol(child.AMPChild):
    "execute a python function from inside worker process"
    def capture_stdout(self):
        "capture stdout into cStringIO"
        sys.stdout = cStringIO.cStringIO()

    def config_node(self, hostname, ip, user, password, identity):
        "configure fabric based on arguments"
        if ip:
            hostname = ip
        env.host_string = user + '@' + hostname
        if password:
            env.password = password
        if identity:
            env.key_filename = identity

    def get_task(self, taskpath):
        "import task from taskpath"
        package, name = taskpath.rsplit('.', 1)
        module = __import__(package, globals(), locals(), name, -1)
        return getattr(module, name)

    @ExecuteTask.responder
    def do_task(self, nodeinfo, taskpath, args, kwargs):
        "execute the job task"
        # load yaml-serialzied parameters
        args = load(args)
        kwargs = load(kwargs)
        self.config_node(*load(nodeinfo))
        # call task
        task = self.get_task(taskpath)
        output = task(*args, **kwargs)
        if not output:
            output = "No output returned."
        return {'output': output}

