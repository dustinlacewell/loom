import os

from twisted.internet.task import LoopingCall

from loom.util import load, dump

class ManifestWatcher(object):
    def __init__(self, callback, *args, **kwargs):
        self.callback = callback
        self.args = args
        self.kwargs = kwargs
        self.files = dict()

    def invoke_callback(self):
        self.callback(*self.args, **self.kwargs)

    def check(self, filepath):
        new_time = os.path.getmtime(filepath)
        if new_time > self.files[filepath]:
            self.invoke_callback()

    def watch(self, filepath):
        self.files[filepath] = os.path.getmtime(filepath)
        LoopingCall(self.check, filepath).start(10)

        
