from fabric.api import run, settings, sudo, open_shell, cd, env, local
from fabric.operations import put, prompt, get

def gethostip(hostname):
    "get ip of hostname"
    output = run('gethostip ' + hostname, true)
    parts = output.split(' ')
    return parts[1]

def run_daemon_cmd(name, command):
    "run a daemon command"
    run("/etc/init.d/%s %s" % (name, command))

def mount(mountpoint):
    "mount specified mountpoint"
    run("mount %s" % (mountpoint, ))

def unmount(mountpoint):
    "unmount specified mountpoint"
    run("umount %s" % (mountpoint, ))

def add_sshfs_mount(*args):
    "install a list of sshfs mountpoints"
    FSTAB_PATTERN = "sshfs#{host}:{remotepath}\t{mountpoint}\tfuse\tdefaults,allow_other,exec,reconnect,transform_symlinks\t0 0"
    for mount in args:
        host = mount['host']
        remotepath = mount['remotepath']
        mountpoint = mount['mountpoint']
        excludes = mount['excludes']
        if env.host in excludes:
            print '%s is excluded from mountpoint.' % (env.host,)
            continue
    
        add_mount_point = True
        tmp_path = '/tmp/fstab.tmp'
        get("/etc/fstab", tmp_path)
        fstab_entry = FSTAB_PATTERN.format(host=host,
                                           remotepath=remotepath,
                                           mountpoint=mountpoint,)
    
        with open(tmp_path, 'r') as file:
            for line in file.readlines():
                if mountpoint in line:
                    add_mount_point = False
        if add_mount_point:
            with open(tmp_path, 'a') as file:
                file.write(fstab_entry + "\n\n")
            put(tmp_path, "/etc/fstab")
        with settings(warn_only=True):
            run('mkdir ' + mountpoint)
            run('umount ' + mountpoint)
            run('mount ' + mountpoint)

    
    
    
