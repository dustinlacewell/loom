loom
====

loom is a server-daemon that provides concurrent task-scheduling for cluster/servers. It consists of a Twisted daemon
that reads in target-node and scheduling information from flexible YAML configuration files. As job schedules come to
bear task work is applied to remote nodes via the Paramiko/SSH API, Fabric. 

installation
------------

in a location of your choice, clone the loom git repository:

  cd ~/
  git clone git://github.com/dustinlacewell/loom.git

nodes.yaml
-----

nodes that can be used in job definitions are declared in a file in the parent directory called **`nodes.yaml'**. The
definitions are quite simple, here's an example:

```yaml
staging:
  user: root
  password: useidentinstead
  ip: 192.168.1.10
```