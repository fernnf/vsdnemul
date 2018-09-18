import logging

from pyroute2 import IPDB, NetNS, IPRoute

from vsdnemul.lib.utils import check_not_null

logger = logging.getLogger(__name__)


def _add_port_ns(ifname, netns, new_name=None):
    check_not_null(ifname, "the interface name cannot be null")
    check_not_null(netns, "the namespace node cannot be null")

    with IPRoute() as ip:
        idx = ip.link_lookup(ifname=ifname)[0]
        if new_name is not None:
            ip.link('set', index=idx, net_ns_fd=netns, ifname=new_name, state="up")
        else:
            ip.link('set', index=idx, net_ns_fd=netns, state="up")

        ip.close()

def _create_pair(ifname, peer, netns=None, mtu=1500):
    check_not_null(ifname, "the interface name cannot be null")
    check_not_null(peer, "the peer interface name cannot be null")

    ip = None
    if netns is None:
        ip = IPDB()
    else:
        ip = IPDB(nl=NetNS(netns))

    ip.create(ifname=ifname, kind="veth", peer=peer)

    with ip.interfaces[ifname] as veth:
        veth.set_mtu(int(mtu))
        veth.up()
        # TODO set veth.set_address( mac_addres)

    if peer is not None:
        with ip.interfaces[peer] as veth_peer:
            veth_peer.set_mtu(int(mtu))
            veth_peer.up()

    ip.release()



def _create_bridge(ifname, slaves:list=None, netns=None, mtu=1500):
    check_not_null(ifname, "the interface name cannot be null")

    ip = None
    if netns is None:
        ip = IPDB()
    else:
        ip = IPDB(nl=NetNS(netns))

    ip.create(kind="bridge", ifname=ifname)

    with ip.interfaces[ifname] as bridge:
        if slaves is not None:
            for intf in slaves:
                bridge.add_port(intf)

            bridge.set_mtu(int(mtu))

        bridge.up()

    ip.release()


def _bridge_add_port(master, slaves=[], netns=None):
    check_not_null(master, "the master bridge name cannot be null")

    ip = None
    if netns is None:
        ip = IPDB()
    else:
        ip = IPDB(nl=NetNS(netns))

    with ip.interfaces[master] as bridge:
        if len(slaves) > 0:
            for interface in slaves:
                bridge.add_node_port(interface)

    ip.release()


def _bridge_del_port(master, slaves=[], netns=None):
    check_not_null(master, "the master bridge name cannot be null")
    ip = None
    if netns is None:
        ip = IPDB()
    else:
        ip = IPDB(nl=NetNS(netns))

    with ip.interfaces[master] as bridge:
        if len(slaves) > 0:
            for interface in slaves:
                bridge.del_node_port(interface)

    ip.release()


def _delete_interface(ifname, netns=None):
    check_not_null(ifname, "the interface name cannot be null")

    ip = None
    if netns is None:
        ip = IPDB()
    else:
        ip = IPDB(nl=NetNS(netns))
    try:
        interface = ip.interfaces[ifname]
        interface.remove().commit()
        ip.release()
    except Exception as ex:
        ip.release()
        raise ValueError("Interface not found {inf} in {node}".format(inf=ifname, node=netns))


def _config_ip_address(ifname, ip_addr, gateway=None, netns=None):
    check_not_null(ifname, "the interface name cannot be null")
    check_not_null(ip_addr, "the ip address of the interface cannot be null")

    ip = None

    if netns is None:
        ip = IPDB()
    else:
        ip = IPDB(nl=NetNS(netns))

    with ip.interfaces[ifname] as interface:
        interface.add_ip(ip_addr)

    if gateway is not None:
        with ip.routes["default"] as route:
            route.gateway = gateway

    ip.release()


def _get_interface_addr(ifname, netns=None):
    check_not_null(ifname, "the interface name cannot be null")

    if netns is None:
        ip = IPDB()
    else:
        ip = IPDB(nl=NetNS(netns))

    with ip.interfaces[ifname] as interface:
        addr = interface.ipaddr[0]["local"]

    ip.release()
    return addr


def _switch_on(ifname, netns=None):
    check_not_null(ifname, "the interface name cannot be null")
    ip = None

    if netns is None:
        ip = IPDB()
    else:
        ip = IPDB(nl=NetNS(netns))

    with ip.interfaces[ifname] as interface:
        interface.up()

    ip.release()


def _switch_off(ifname, netns=None):
    check_not_null(ifname, "the interface name cannot be null")
    ip = None

    if netns is None:
        ip = IPDB()
    else:
        ip = IPDB(nl=NetNS(netns))

    with ip.interfaces[ifname] as interface:
        interface.down()

    ip.release()


def create_pair(ifname, peer, netns=None, mtu=1500):
    try:
        _create_pair(ifname=ifname, peer=peer, netns=netns, mtu=mtu)
        return True
    except Exception as ex:
        logger.error(ex.__cause__)
        return False


def create_bridge(ifname, slaves:list=None, netns=None, mtu=1500):
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
        logger.error(ex.args[0])
        return False


def add_port_ns(ifname, netns, new_name=None):
    try:
        _add_port_ns(ifname=ifname, netns=netns, new_name=new_name)
        return True
    except Exception as ex:
        logger.error(ex.__cause__)
        return False


def config_port_address(ifname, ip_addr, gateway=None, netns=None):
    try:
        _config_ip_address(ifname=ifname, ip_addr=ip_addr, gateway=gateway, netns=netns)
    except Exception as ex:
        logger.error(ex.__cause__)


def get_interface_addr(ifname, netns=None):
    return _get_interface_addr(ifname=ifname, netns=netns)


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