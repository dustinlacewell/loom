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

loom.yaml
---------

The main configuration format for Loom is YAML. When Loom starts it will search a few paths for the main configuration file, usually **~/.loom.yaml** If you have a special need to place this file elsewhere you can specify it with the -c/--config commandline option. Some configuration options are required and tell Loom where to find your **node** and **job** manifests. Other options are optional, like **datafile** which contains YAML that will be prepended to each of your job-manifests. We'll describe the datafile option later. Here are some of the important options you can specify:

 + **nodesfile** : Path to your node-manifest file
 + **jobspath** : Path containing your job-manifests
 + **datafile** : Path to your data-manifest containing YAML to be prepended to each job-manifest

nodesfile
---------

nodes that can be used in job definitions are declared in a file specified by the **nodesfile** setting. The definitions are quite simple. The YAML key should be the locally resolvable hostname of the node and is the name used to refer to the node in the job manifests. In this example it it is **staging**:

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

jobspath
--------

In Loom, jobs are the combination of a cron-schedule, a list of target nodes and a python import path that designates the callable that should be applied to each node. The **jobspath** configuration option should specify a path where your job-manifests can be found. This path will be searched recursively for any files ending in the extension **.yaml** that contain a top-level YAML dictionary key **jobs**. The value should be a dictionary with each key being the name of a job. The job definition should follow. Here is the example job manifest that ships with Loom:

```yaml
jobs:
    mountstorage:
        task: loom.system.add_sshfs_mount
        args: [*storage]
        schedule: "* * * * *"
        targets: [staging, production]
        description: Mount storage on forge and hive
    testtask:
        task: fabric.api.run
        args: ["touch /tmp/loom_was_here"]
        schedule: "* * * * *"
        targets: *dbservers
        description: Leave our mark
```

The structure is quite simple and allows you to very expressively describe the parameters of a scheduled job. You'll notice that, say in the case of **mountstorage** that the **args** parameter contains a YAML reference. The **testtask** targets are also specified as a YAML reference. These references may be defined in your **datafile** and referred to in multiple places in your manifests. The datafile will be described shortly. First though, let's go through the job parameters that you can specify:

 + **YAML key** : Job name
 + **task** : a Python import path pointing to a Python ''callable'' (usually a Fabric task)
 + **args** : a list of values to pass as arguments to the task callable
 + **kwargs** : a dictionary of values to pass as keyword-arguments to the task callable
 + **schedule** : a regular cron scheduling definition
 + **targets** : a list of node names, defined in your nodesfile
 + **description** : textual description of the job