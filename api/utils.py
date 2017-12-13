import os
import subprocess
import ipaddress
from pyroute2 import IPDB, NetNS
import uuid


def check_not_null(value, msg):
    if value is None:
        raise TypeError(msg)
    else:
        return value


def create_namespace(pid=int):

    if not os.path.exists("/var/run/netns"):
        os.mkdir("/var/run/netns")

    dir_src = "/proc/{pid}/ns/net".format(pid = pid)
    dir_tgt = "/var/run/netns/{pid}".format(pid = pid)

    if os.path.exists(dir_src):
        os.symlink(dir_src, dir_tgt)


def delete_namespace(pid=int):
        if os.path.exists("/var/run/netns"):
            if os.path.exists("/var/run/netns/{pid}".format(pid = pid)):
                os.remove("/var/run/netns/{pid}".format(pid = pid))
            else:
                OSError("namespace with pid not exist")
        else:
            raise OSError("folder namespace not exist")


def is_valid_ip(addr):
    try:
        ipaddress.ip_address(address = addr)
        return True
    except Exception as ex:
        raise ValueError("Error: "+ex.args[0])


def equals_ignore_case(a, b):
    return a.upper() == b.upper()

