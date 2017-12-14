import ipaddress
import os
import names


def check_not_null(value, msg):
    if value is None:
        raise TypeError(msg)
    else:
        return value


def create_namespace(name: str, pid: int):
    if not os.path.exists("/var/run/netns"):
        os.mkdir("/var/run/netns")

    dir_src = "/proc/{pid}/ns/net".format(pid = pid)
    dir_tgt = "/var/run/netns/{name}".format(name = name)

    if os.path.exists(dir_src):
        os.symlink(dir_src, dir_tgt)
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
