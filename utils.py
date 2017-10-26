import os
import pyroute2

def CheckNotNull(value, msg):
    if value is None:
        raise TypeError(msg)
    else:
        return value


def CreateNamspace(pid=int):

    if not os.path.exists("/var/run/netns"):
        os.mkdir("/var/run/netns")

    dir_src = "/proc/{pid}/ns/net".format(pid = pid)
    dir_tgt = "/var/run/netns/{pid}".format(pid = pid)

    os.symlink(source = dir_src, target_is_directory = dir_tgt)

def DeleteNamespace(pid=int):
        if os.path.exists("/var/run/netns"):
            if os.path.exists("/var/run/netns/{pid}".format(pid = pid)):
                os.rmdir("/var/run/netns/{pid}".format(pid = pid))
            else:
                OSError("namespace with pid not exist")
        else:
            raise OSError("folder namespace not exist")

def CreateVethLinkContainers(src_pid, tgt_pid, src_ifname, tgt_ifname):

    ip = pyroute2.IPDB()
    ip.create(kind = "veth", ifname = src_ifname, peer = tgt_ifname)

    with ip.