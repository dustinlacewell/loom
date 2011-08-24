Loom
====

Loom is a server-daemon that provides concurrent task-scheduling for clusters and servers. It consists of a Twisted daemon
that reads in target-node and scheduling information from flexible YAML configuration files. As job schedules come to
bear, task-work is applied to remote nodes via the Paramiko/SSH API, Fabric. Tasks applied to multiple nodes are
applied to each node seperately in a child-process allowing Loom to provide Fabric with some measure of concurrency.

installation
------------

in a location of your choice, clone the Loom git repository:

    cd ~/
    git clone git://github.com/dustinlacewell/loom.git
    cd loom
    sudo python setup.py install

loom.yaml
---------
The main configuration format for Loom is YAML. When Loom starts it will search a few paths for the main configuration file, usually **~/.loom.yaml** If you have a special need to place this file elsewhere you can specify it with the -c/--config commandline option. Some configuration options are required and tell Loom where to find your **node** and **job** manifests. Other options are optional, like **datafile** which contains YAML that will be prepended to each of your job-manifests. We'll describe the datafile option later. Here are some of the important options you can specify:

 + **nodesfile** : Path to your node-manifest file
 + **jobspath** : Path containing your job-manifests
 + **datafile** : Path to your data-manifest containing YAML to be prepended to each job-manifest
 + **min_workers**: Minimum amount of child worker-processes to maintain (default: 0)
 + **max_workers**: Maximum amount of child worker-processes to maintain (default: 10)

nodesfile
---------
nodes that can be used in job definitions are declared in a file specified by the **nodesfile** setting. The definitions are quite simple. The YAML key should be the locally resolvable hostname of the node and is the name used to refer to the node in the job manifests. In this example it it is **staging**:

```yaml
staging:
  user: root
  password: useidentinstead
  ip: 192.168.1.10
```

If your loom user on the server that hosts your loom instance is already setup for passwordless SSH access to your nodes and the nodes have locally configured hostnames (/etc/hosts) then a node manifest can be as simple as:

```yaml
staging: # node name will resolve to ip
  user: root # user still needs to be supplied
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

The structure is quite simple and allows you to describe the parameters of a scheduled job. You'll notice that, say in the case of  the **mountstorage** job that the **args** parameter contains a YAML reference. The **testtask** job's targets are also specified as a YAML reference. These references may be defined in your **datafile** and referred to in multiple places in your manifests. The datafile will be described shortly. First though, let's go through the job parameters that you can specify:

 + **YAML key** : job name
 + **task** : a Python import path pointing to a Python ''callable'' (usually a Fabric task)
 + **args** : a list of values to pass as arguments to the task callable
 + **kwargs** : a dictionary of values to pass as keyword-arguments to the task callable
 + **schedule** : a regular cron scheduling definition
 + **targets** : a list of node names, defined in your nodesfile
 + **description** : textual description of the job


datafile
--------
The datafile is a special file that contains YAML data that will be prepended to all of your job-manifests before being processed. This allows you to define certain complex data as **YAML Anchors**  that can be resued througout your manifests. If you need to pass complex values to your task callables this is a good place to define it. Of course you are not limited to putting your complex data here. Each job-manifest can contain it's own YAML Anchors however they will only be available from that specific manifest. Here is the contents of the example datafile shipped with loom:

```yaml
hosts: 
    - &cloudhosts [staging, production]
    - &dbservers [db1, db2, db3, db4]
mountpoints:
    - &storage
        host: root@staging
        remotepath: /mnt/storage
        mountpoint: /mnt/storage
        excludes: [staging]
    - &rootutils
        host: root@staging
        remotepath: /mnt/rootutils
        mountpoint: /mnt/rootutils
        excludes: [staging]
```

You can see that we have defined collections for our different node types and a couple structures claiming to be mountpoints. The hosts anchors are easy to understand. They allow you to categorically refer to your defined nodes with a single identifier. The mountpoints however are not data that is specifically relevant to Loom. It is data that is passed to your job tasks as argument values. If you scroll up, you can see that we refer to the **storage** mountpoint as the **args** parameter in the **mountstorage** job-manifest. Pretty handy.

starting the daemon
-------------------

Loom is built and packaged as a Twisted plugin and so the **'twistd'** command is used to interact with it. After writing your loom config and node and job manifests you can start loom with the following command:

    twistd loom -c <path-to-your-loom-config>
    
Or if you'd like to see the output on stdout:

    twistd -n loom -c <path-to-your-loom-config>
    
current outstanding issues
--------------------------

### logging
 + Ampoule spams the twisted log and doesn't use the "system" keyword so that its messages can be filtered. Ampoule will probably need to be patched to fix this.
 + Each job manifest should take a log option and we should route job output there
 + Logging in general is unhandled and not investigated at this point
 
 