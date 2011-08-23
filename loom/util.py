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

