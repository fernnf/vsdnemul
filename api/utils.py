import ipaddress
import random
from pathlib import Path

import names


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
    dir_tgt = Path("/var/run/netns")
    file_tgt = Path("/var/run/netns/{name}".format(name = name))

    if dir_tgt.exists():
        if file_tgt.is_symlink():
            file_tgt.unlink()
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


def rand_interface_name():

    digits = 8
    lower = 10 ** (digits - 1)
    upper = 10 ** digits - 1

    return str(random.randint(lower, upper))
