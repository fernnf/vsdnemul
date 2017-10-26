import os
from pyroute2 import IPDB, NetNS


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

    os.symlink(source = dir_src, target_is_directory = dir_tgt)


def delete_namespace(pid=int):
        if os.path.exists("/var/run/netns"):
            if os.path.exists("/var/run/netns/{pid}".format(pid = pid)):
                os.rmdir("/var/run/netns/{pid}".format(pid = pid))
            else:
                OSError("namespace with pid not exist")
        else:
            raise OSError("folder namespace not exist")


def create_veth_link_containers(src_pid, tgt_pid, src_ifname, tgt_ifname):
    with IPDB() as ipdb:
        ipdb.create(kind = "veth", ifname = src_ifname, peer = tgt_ifname).commit()
        with ipdb.interfaces[src_ifname] as source:
            source.net_ns_fd = src_pid
        with ipdb.interfaces[tgt_ifname] as target:
            target.net_ns_fd = tgt_pid

    with IPDB(nl = NetNS(src_pid)) as nsdb:
        with nsdb.interfaces[src_ifname] as source:
            source.up()
            source.set_mtu(9000)

    with IPDB(nl = NetNS(tgt_pid)) as nsdb:
        with nsdb.interfaces[src_ifname] as source:
            source.up()
            source.set_mtu(9000)


def delete_veth_link_containers(src_pid, tgt_pid, src_ifname, tgt_ifname):
    with IPDB(nl = NetNS(src_pid)) as nsdb:
        nsdb.interfaces[src_ifname].remove().commit()

    with IPDB(nl = NetNS(tgt_pid)) as nsdb:
        if nsdb.interfaces.get(tgt_ifname) is not None:
            nsdb.interfaces.get(tgt_ifname).remove().commit()


def config_interface_address(pid, if_name, addr, gateway = None):
    with IPDB(nl = NetNS(pid)) as nsdb:
        with nsdb.interfaces[if_name] as intf:
            intf.add_ip(addr)
        if gateway is not None:
            with nsdb.routes['default'] as route:
                route.gateway = gateway
