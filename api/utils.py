import ipaddress
import os
import names
from pathlib import Path

def check_not_null(value, msg):
    if value is None:
        raise TypeError(msg)
    else:
        return value


def create_namespace(name: str, pid: int):

    dir_dest = Path("/var/run/netns")
    dir_src = Path("/proc/{pid}/ns/net".format(pid = pid))
    dir_tgt = Path("/var/run/netns/{name}".format(name = name))

    if not dir_dest.exists():
        dir_dest.mkdir()

    if dir_src.exists():
        if dir_tgt.is_symlink():
            dir_tgt.unlink()
        dir_tgt.symlink_to(dir_src.as_posix())
    else:
        OSError("the namespace not exist")


def delete_namespace(name: str):
    dir_tgt = "/var/run/netns/{name}".format(name = name)

    if os.path.exists("/var/run/netns"):
        if os.path.exists(dir_tgt):
            os.remove(dir_tgt)
        else:
            OSError("namespace with name not exist")
    else:
        raise OSError("folder namespace not exist")


def clean_namespaces():
    delete_namespace("*")


def is_valid_ip(addr: str):
    try:
        ipaddress.ip_address(address = addr)
        return True
    except Exception as ex:
        raise ValueError("Error: " + ex.args[0])


def equals_ignore_case(a: str, b: str):
    return a.upper() == b.upper()


def rand_name():
    return names.get_first_name().lower()
