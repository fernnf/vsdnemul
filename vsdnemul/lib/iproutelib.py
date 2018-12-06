import logging
from ipaddress import IPv4Interface
import traceback

from pyroute2 import IPRoute, NetNS

from vsdnemul.lib.utils import check_not_null

logger = logging.getLogger(__name__)


def _add_port_ns(ifname, netns, new_name=None):
    check_not_null(ifname, "the interface name cannot be null")
    check_not_null(netns, "the namespace node cannot be null")

    with IPRoute() as ipr:
        idx = ipr.link_lookup(ifname=ifname)[0]
        if new_name is not None:
            ipr.link('set', index=idx, net_ns_fd=netns, ifname=new_name, state="up")
        else:
            ipr.link('set', index=idx, net_ns_fd=netns, state="up")




def _create_pair(ifname, peer, netns=None, mtu=1500):
    check_not_null(ifname, "the interface name cannot be null")
    check_not_null(peer, "the peer interface name cannot be null")


    def create():
        with IPRoute() as ipr:
            ipr.link("add", ifname=ifname, kind="veth", peer=peer)

            ifnet = ipr.link_lookup(ifname=ifname)[0]
            ifpeer = ipr.link_lookup(ifname=peer)[0]

            ipr.link("set", index=ifnet,  mtu=mtu)
            ipr.link("set", index=ifnet, state="up")
            ipr.link("set", index=ifpeer, mtu=mtu)
            ipr.link("set", index=ifpeer, state="up")



    def create_ns():
        with NetNS(netns=netns) as ipr:
            ipr.link("add", ifname=ifname, kind="veth", peer=peer)

            ifnet = ipr.link_lookup(ifname=ifname)[0]
            ifpeer = ipr.link_lookup(ifname=peer)[0]

            ipr.link("set", index=ifnet, mtu=mtu)
            ipr.link("set", index=ifnet, state="up")
            ipr.link("set", index=ifpeer, mtu=mtu)
            ipr.link("set", index=ifpeer, state="up")



    if netns is None:
        create()
    else:
        create_ns()

def _create_bridge(ifname, slaves=None, netns=None, mtu=1500):
    check_not_null(ifname, "the interface name cannot be null")


    def create():
        with IPRoute() as ipr:
            ipr.link("add", ifname=ifname, kind="bridge")

            inet = ipr.link_lookup(ifname=ifname)[0]
            ipr.link("set", index=inet, mtu=mtu)

            if slaves is not None:
                for i in slaves:
                    port = ipr.link_lookup(ifname=i)[0]
                    ipr.link("set", index=port, master=inet)

            ipr.link("set", index=inet, state="up")


    def create_ns():
        with NetNS(netns=netns) as ipr:
            ipr.link("add", ifname=ifname, kind="bridge")

            inet = ipr.link_lookup(ifname=ifname)[0]
            ipr.link("set", index=inet, mtu=mtu)

            if slaves is not None:
                for i in slaves:
                    port = ipr.link_lookup(ifname=i)[0]
                    ipr.link("set", index=port, master=inet)

            ipr.link("set", index=inet, state="up")


    if netns is None:
        create()
    else:
        create_ns()


def _bridge_add_port(master, slaves=[], netns=None):
    check_not_null(master, "the master bridge name cannot be null")

    def addport():
        with IPRoute() as ipr:
            inet = ipr.link_lookup(ifname=master)[0]

            for i in slaves:
                slave = ipr.link_lookup(ifname=i)[0]
                ipr.link("set", index=slave, master=inet)



    def addporns():
        with NetNS(netns=netns) as ipr:
            inet = ipr.link_lookup(ifname=master)[0]

            for i in slaves:
                slave = ipr.link_lookup(ifname=i)[0]
                ipr.link("set", index=slave, master=inet)



    if netns is None:
        addport()
    else:
        addporns()

def _bridge_del_port(master, slaves=[], netns=None):
    check_not_null(master, "the master bridge name cannot be null")

    def delport():
        with IPRoute() as ipr:
            for i in slaves:
                slave = ipr.link_lookup(ifname=i)[0]
                ipr.link("set", index=slave, master=0)



    def delportns():
        with NetNS(netns=netns) as ipr:
            for i in slaves:
                slave = ipr.link_lookup(ifname=i)[0]
                ipr.link("set", index=slave, master=0)

    if netns is None:
        delport()
    else:
        delportns()

def _delete_interface(ifname, netns=None):
    check_not_null(ifname, "the interface name cannot be null")

    def delport():
        with IPRoute() as ipr:
            inet = ipr.link_lookup(ifname=ifname)[0]
            ipr.link("del", index=inet)


    def delportns():
        with NetNS(netns=netns) as ipr:
            inet = ipr.link_lookup(ifname=ifname)[0]
            ipr.link("del", index=inet)


    if netns is None:
        delport()
    else:
        delportns()

def _config_ip_address(ifname, ip_addr, mask, gateway=None, netns=None):
    check_not_null(ifname, "the interface name cannot be null")
    check_not_null(ip_addr, "the ip address of the interface cannot be null")

    def configip():
        with IPRoute() as ipr:
            inet = ipr.link_lookup(ifname=ifname)[0]
            ipr.addr("add", index=inet, address=ip_addr, mask=int(mask))

            if gateway is not None:
                ipr.route("add", dst="default", gateway=gateway)



    def configipns():
        with NetNS(netns=netns) as ipr:
            inet = ipr.link_lookup(ifname=ifname)[0]
            ipr.addr("add", index=inet, address=ip_addr, mask=int(mask))

            if gateway is not None:
                ipr.route("add", dst="default", gateway=gateway)


    if netns is None:
        configip()
    else:
        configipns()



def _get_interface_addr(ifname, netns=None):
    check_not_null(ifname, "the interface name cannot be null")

    def get_addr():
        with IPRoute() as ipr:
            inet = ipr.get_addr(label=ifname)
            ret = inet[0]["attrs"][0][1]
            return ret

    def get_ns_addr():
        with NetNS(netns=netns) as ipr:
            inet = ipr.get_addr(label=ifname)
            ret = inet[0]["attrs"][0][1]
            return ret

    return (get_addr() if netns is None else get_ns_addr())

def _get_interface_mac(ifname, netns=None):
    check_not_null(ifname, "the interface name cannot be null")

    def get_mac():
        with IPRoute() as ipr:
            idx = ipr.link_lookup(ifname=ifname)
            inet = ipr.link("get", index=idx)
            ret = inet[0]['attrs'][18][1]
            return ret
    def get_mac_ns():
        with NetNS(netns=netns) as ipr:
            idx = ipr.link_lookup(ifname=ifname)
            inet = ipr.link("get", index=idx)
            ret = inet[0]['attrs'][19][1]
            return ret

    return (get_mac() if netns is None else get_mac_ns())

def _switch_on(ifname, netns=None):
    check_not_null(ifname, "the interface name cannot be null")

    def switchon():
        with IPRoute() as ipr:
            inet = ipr.link_lookup(ifname=ifname)[0]
            ipr.link("set", index=inet, state="up")
            ipr.close()

    def switchonns():
        with NetNS(netns=netns) as ipr:
            inet = ipr.link_lookup(ifname=ifname)[0]
            ipr.link("set", index=inet, state="up")
            ipr.close()

    if netns is None:
        switchon()
    else:
        switchonns()


def _switch_off(ifname, netns=None):
    check_not_null(ifname, "the interface name cannot be null")

    def switchoff():
        with IPRoute() as ipr:
            inet = ipr.link_lookup(ifname=ifname)[0]
            ipr.link("set", index=inet, state="down")
            ipr.close()

    def switchoffns():
        with NetNS(netns=netns) as ipr:
            inet = ipr.link_lookup(ifname=ifname)[0]
            ipr.link("set", index=inet, state="down")
            ipr.close()

    if netns is None:
        switchoff()
    else:
        switchoffns()


def create_pair(ifname, peer, netns=None, mtu=1500):
    try:
        _create_pair(ifname=ifname, peer=peer, netns=netns, mtu=mtu)
        return True
    except Exception as ex:
        logger.error(ex.__cause__)
        return False


def create_bridge(ifname, slaves: list = None, netns=None, mtu=1500):
    try:
        _create_bridge(ifname=ifname, slaves=slaves, netns=netns, mtu=mtu)
        return True
    except Exception as ex:
        logger.error(ex.__cause__)
        return False


def bridge_add_port(master, slaves=[], netns=None):
    try:
        _bridge_add_port(master=master, slaves=slaves, netns=netns)
        return True
    except Exception as ex:
        logger.error(ex.__cause__)
        return False


def bridge_del_port(master, slaves=[], netns=None):
    try:
        _bridge_del_port(master=master, slaves=slaves, netns=netns)
        return True
    except Exception as ex:
        logger.error(ex.__cause__)
        return False


def delete_port(ifname, netns=None):
    try:
        _delete_interface(ifname=ifname, netns=netns)
        return True
    except Exception as ex:
        logger.error(ex)
        return False


def add_port_ns(ifname, netns, new_name=None):
    try:
        _add_port_ns(ifname=ifname, netns=netns, new_name=new_name)
        return True
    except Exception as ex:
        logger.error(ex.__cause__)
        return False


def config_port_address(ifname, ip_addr, mask, gateway=None, netns=None):
    try:
        _config_ip_address(ifname=ifname, ip_addr=ip_addr, mask=mask, gateway=gateway, netns=netns)
    except Exception as ex:
        logger.error(ex.__cause__)


def get_interface_addr(ifname, netns=None):
    return _get_interface_addr(ifname=ifname, netns=netns)


def get_interface_mac(ifname, netns=None):
    return _get_interface_mac(ifname, netns)

def switch_on(ifname, netns=None):
    try:
        _switch_on(ifname=ifname, netns=netns)
    except Exception as ex:
        logger.error(ex.args[0])


def switch_off(ifname, netns=None):
    try:
        _switch_off(ifname=ifname, netns=netns)
    except Exception as ex:
        logger.error(ex.__cause__)
