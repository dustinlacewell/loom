loom
====

loom is a server-daemon that provides concurrent task-scheduling for clusters and servers. It consists of a Twisted daemon
that reads in target-node and scheduling information from flexible YAML configuration files. As job schedules come to
bear, task-work is applied to remote nodes via the Paramiko/SSH API, Fabric. Tasks applied to multiple nodes are
applied to each node seperately in a child-process allowing Loom to provide Fabric with some measure of concurrency.

installation
------------

in a location of your choice, clone the loom git repository:

    cd ~/
    git clone git://github.com/dustinlacewell/loom.git

nodes.yaml
----------

nodes that can be used in job definitions are declared in a file in the parent directory called **`nodes.yaml'**. The
definitions are quite simple. The YAML key is the should be the locally resolvable hostname of the node. Here's an example:

```yaml
staging:
  user: root
  password: useidentinstead
  ip: 192.168.1.10
```

### node attributes

here are a list of all possible node attributes:

 + **YAML key**: the locally resolvable hostname
 + **ip**: override hostname with specified IP address
 + **user**: user under which node work will take place
 + **password**: password for user above
 + **identity**: a locally accessible ssh identity to use instead of user/password