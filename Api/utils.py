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


def delete_interface(if_name):
    delete = "/usr/sbin/ip link delete {name} "
    exec_cmd(delete)


def set_mtu_interface(if_name, mtu):
    set_mtu = "/usr/sbin/ip link set {name} mtu {mtu}".format(name = if_name, mtu = mtu)
    exec_cmd(set_mtu)


def set_master_interface(if_name, br_name):
    set_master = "/usr/sbin/ip link set {if_name} master {br_name}".format(if_name = if_name, br_name = br_name)
    exec_cmd(set_master)


def set_interface_up(if_name):
    set_up = "/usr/sbin/ip link set {if_name} up".format(if_name = if_name)
    exec_cmd(set_up)


def set_interface_down(if_name):
    set_down = "/usr/sbin/ip link set {if_name} up".format(if_name = if_name)
    exec_cmd(set_down)


def add_ns_interface(ns_pid,if_name):
    set_ns_interface = "/usr/sbin/ip link set {if_name} netns {pid}".format(if_name = if_name, pid = ns_pid)
    exec_cmd(set_ns_interface)


def set_addr_interface(addr, if_name):
    set_addr = "/usr/sbin/ip addr add {addr} dev {if_name}".format(addr = addr, if_name = if_name)
    exec_cmd(set_addr)


def set_ns_addr_interface(ns_pid, addr,if_name):
    set_ns_addr = "/usr/sbin/ip netns exec {pid} ip addr add {addr} dev {if_name}".format(pid = ns_pid, addr = addr,
                                                                                          if_name = if_name)
    exec_cmd(set_ns_addr)


def set_ns_interface_up(ns_pid, if_name):
    set_ns_up = "/usr/sbin/ip netns exec {pid} ip link set {if_name} up".format(pid = ns_pid, if_name = if_name)
    exec_cmd(set_ns_up)


def set_ns_interface_down(ns_pid, if_name):
    set_ns_down = "/usr/sbin/ip netns exec {pid} ip link set {if_name} down".format(pid = ns_pid, if_name = if_name)
    exec_cmd(set_ns_down)


def exec_cmd(cmd):
    proc = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    ret = proc.wait()
    if not ret == 0:
        outs, errs = proc.communicate()
        raise OSError(errs.decode())


def create_veth_link_containers(src_pid, tgt_pid, src_name, tgt_name, link_name):

    ifname = "{src}-{dst}"

    src_ifname = ifname.format(src= src_name, dst = tgt_name)
    src_peer = ifname.format(src= src_name, dst = link_name)

    tgt_ifname = ifname.format(src= tgt_name, dst = src_name)
    tgt_peer = ifname.format(src = tgt_name, dst = link_name)

    create_interface(if_name = src_ifname, type = "veth", peer = src_peer, mtu = "9000")
    create_interface(if_name = tgt_ifname, type = "veth", peer = tgt_peer, mtu = "9000")

    create_interface(if_name = link_name)

    set_master_interface(if_name = src_peer, br_name = link_name)
    set_master_interface(if_name = tgt_peer, br_name = link_name)
    set_mtu_interface(if_name = link_name, mtu = "9000")

    add_ns_interface(ns_pid = src_pid, if_name = src_ifname)
    add_ns_interface(ns_pid = tgt_pid, if_name = tgt_ifname)

    set_ns_interface_up(ns_pid = src_pid, if_name = src_ifname)
    set_ns_interface_up(ns_pid = tgt_pid, if_name = tgt_ifname)

    set_interface_up(if_name = src_peer)
    set_interface_up(if_name = tgt_peer)
    set_interface_up(if_name = link_name)


def delete_veth_link_containers(src_name, tgt_name, link_name):

    ifname = "{src}-{dst}"

    src_peer = ifname.format(src = src_name, dst = link_name)
    tgt_peer = ifname.format(src = tgt_name, dst = link_name)

    delete_interface(if_name = link_name)
    delete_interface(if_name = src_peer)
    delete_interface(if_name = tgt_peer)


def config_interface_address(pid, if_name, addr):
    set_ns_addr_interface(ns_pid = pid, if_name = if_name, addr = addr)


def is_valid_ip(addr):
    try:
        ipaddress.ip_address(address = addr)
        return True
    except Exception as ex:
        raise ValueError("Error: "+ex.args[0])


def equals_ignore_case(a, b):
    return a.upper() == b.upper()


def create_interface(if_name, type="bridge", peer=None, mtu = "1500"):
    create = "/usr/sbin/ip link add name {name}".format(name = if_name)

    if type.__eq__("bridge"):
        create = create+" type {type}".format(type = type)
        exec_cmd(create)

    elif type.__eq__("veth"):
        if peer is not None:
            create = create+" mtu {mtu} type {type} peer name {peer} mtu {mtu}".format(type = type, peer = peer,
                                                                                       mtu = mtu)
            exec_cmd(create)
    else:
        raise ValueError("the type value is unknown")


