from loom import amp

def load(filename):
    nodes = {}
    with open(filename, 'r') as yaml:
        data = amp.load(yaml)
    for hostname, node in data.items():
        nodes[hostname] = LoomNode(hostname, **node)
    return nodes

class LoomNode(object):
    def __init__(self, hostname, **kwargs):
        self.hostname = hostname
        self.user = kwargs['user']
        self.ip = kwargs.get('ip', '')
        self.password = kwargs.get('password', '')
        self.identity = kwargs.get('identity', '')

    def __amp__(self):
        return amp.dump((self.hostname,
                self.ip,
                self.user,
                self.password,
                self.identity))
