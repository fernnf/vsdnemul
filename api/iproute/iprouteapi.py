from pyroute2 import IPDB, NetNS

from api.utils import check_not_null


def _add_port_ns(ifname, netns):
    check_not_null(ifname, "the interface name cannot be null")
    check_not_null(netns, "the namespace node cannot be null")

    ip = IPDB()

    with ip.interfaces[ifname] as ns:
        ns.net_ns_fd = ifname

    ip.release()


def _create_pair(ifname, peer, netns = None, mtu = 1500):
    check_not_null(ifname, "the interface name cannot be null")
    check_not_null(ifname, "the peer interface name cannot be null")
    ip = None
    if netns is None:
        ip = IPDB()
    else:
        ip = IPDB(nl = NetNS(netns))

    ip.create(ifname = ifname, kind = "veth", peer = peer).commit()

    with ip.interfaces[ifname] as veth:
        veth.set_mtu(mtu)
        veth.up()

    if peer is not None:
        with ip.interfaces[peer] as veth_peer:
            veth_peer.set_mtu(mtu)
            veth_peer.up()

    ip.release()


def _create_bridge(ifname, slaves = [], mtu = 1500, netns = None):
    check_not_null(ifname, "the interface name cannot be null")

    ip = None
    if netns is None:
        ip = IPDB()
    else:
        ip = IPDB(nl = NetNS(netns))

    ip.create(kind = "bridge", ifname = ifname).commit()

    with ip.interfaces[ifname] as bridge:
        if len(slaves) > 0:
            for intf in slaves:
                bridge.add_port_br(intf)

            bridge.set_mtu(mtu)
            bridge.up()

        bridge.up()

    ip.release()


def _bridge_add_port(master, slaves = [], netns = None):
    check_not_null(master, "the master bridge name cannot be null")

    ip = None
    if netns is None:
        ip = IPDB()
    else:
        ip = IPDB(nl = NetNS(netns))

    with ip.interfaces[master] as bridge:
        if len(slaves) > 0:
            for interface in slaves:
                bridge.add_port_br(interface)

    ip.release()


def _bridge_del_port(master, slaves = [], netns = None):
    check_not_null(master, "the master bridge name cannot be null")
    ip = None
    if netns is None:
        ip = IPDB()
    else:
        ip = IPDB(nl = NetNS(netns))

    with ip.interfaces[master] as bridge:
        if len(slaves) > 0:
            for interface in slaves:
                bridge.del_port(interface)

    ip.release()


def _delete_interface(ifname, netns = None):
    check_not_null(ifname, "the interface name cannot be null")

    ip = None
    if netns is None:
        ip = IPDB()
    else:
        ip = IPDB(nl = NetNS(netns))

    ip.interfaces[ifname].remove().commit()
    ip.release()


def _config_ip_address(ifname, ip_addr, gateway = None, netns = None):
    ip = None
    if netns is None:
        ip = IPDB()
    else:
        ip = IPDB(nl = NetNS(netns))

    with ip.interfaces[ifname] as interface:
        interface.add_ip(ip_addr)

    if gateway is not None:
        with ip.routes["default"] as route:
            route.gateway = gateway

    ip.release()


class IpRouteApi(object):

    @staticmethod
    def create_pair(ifname, peer, netns = None, mtu = 1500):
        try:
            _create_pair(ifname, peer, netns, mtu)
            return True
        except Exception as ex:
            return False

    @staticmethod
    def create_bridge(ifname, slaves = [], mtu = 1500, netns = None):

        try:
            _create_bridge(ifname, slaves, mtu, netns)
            return True
        except Exception as ex:
            return False

    @staticmethod
    def bridge_add_port(master, slaves = [], netns = None):
        try:
            _bridge_add_port(master, slaves, netns)
            return True
        except Exception as ex:
            return False

    @staticmethod
    def bridge_del_port(master, slaves = [], netns = None):
        try:
            _bridge_del_port(master, slaves, netns)
            return True
        except Exception as ex:
            return False

    @staticmethod
    def delete_interface(ifname, netns = None):
        try:
            _delete_interface(ifname, netns)
            return True
        except Exception as ex:
            return False

    @staticmethod
    def config_ip_address(ifname, ip_addr, gateway = None, netns = None):
        try:
            _config_ip_address(ifname, ip_addr, gateway, netns)
            return True
        except Exception as ex:
            return False

    @staticmethod
    def add_port_ns(ifname, netns):
        try:
            _add_port_ns(ifname = ifname, netns = netns)
            return True
        except Exception as ex:
            return False

