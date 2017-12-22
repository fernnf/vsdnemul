import uuid
import random

from api.iproute.iprouteapi import IpRouteApi
from api.link.linkapi import Link, LinkType
from api.log.logapi import get_logger
from api.ovsdb.ovsdbapi import OvsdbApi
from api.utils import rand_interface_name, check_not_null


logger_direct = get_logger("DirectLinkBridge")


class DirectLinkBridge(Link):

    def __init__(self, id, node_source, node_target, port_source, port_target,bridge_ns = "switch0", mtu = "1500"):
        check_not_null(id, "the id link cannot be null")

        super().__init__(node_source = node_source, node_target = node_target, type = LinkType.DIRECT,
                         port_target = port_target, port_source = port_source)
        self._bridge_ns = bridge_ns
        self._mtu = mtu
        self._id = id

    def create(self):

        peer_src = self.port_target.peer()
        peer_dst = self.port_source.peer()
        link_bridge = "link{id}".format(id = self._id)

        try:

            IpRouteApi.create_pair(ifname = self.port_source.name, peer = peer_src, mtu = self._mtu)
            IpRouteApi.create_pair(ifname = self.port_target.name, peer = peer_dst, mtu = self._mtu)
            IpRouteApi.create_bridge(ifname = link_bridge, slaves = [peer_src, peer_dst], mtu = self._mtu)
            IpRouteApi.add_port_ns(ifname = self.port_source.name, netns = self.node_source)
            IpRouteApi.add_port_ns(ifname = self.port_target.name, netns = self.node_target)
            IpRouteApi.switch_on(ifname = self.port_source.name, netns = self.node_source)
            IpRouteApi.switch_on(ifname = self.port_target.name, netns = self.node_target)
            OvsdbApi.add_port_br(bridge = self._bridge_ns, netns = self.node_source, port_name = self.port_source)
            OvsdbApi.add_port_br(bridge = self._bridge_ns, netns = self.node_target, port_name = self.port_target)

        except Exception as ex:
            logger_direct.error(str(ex.args))

    def delete(self):

        link_bridge = "link{id}".format(id = self._id)

        try:
            IpRouteApi.delete_port(ifname = self.port_source, netns = self.node_source)
            IpRouteApi.delete_port(ifname = self.port_target, netns = self.node_target)
            OvsdbApi.del_port_br(bridge = self._bridge_ns, port_name = self.port_source, netns = self.node_source)
            OvsdbApi.del_port_br(bridge = self._bridge_ns, port_name = self.port_target, netns = self.node_target)
            IpRouteApi.delete_port(ifname = link_bridge)

        except Exception as ex:
            logger_direct.error(str(ex.args))


logger_host = get_logger("HostLinkBridge")


class HostLinkBridge(Link):
    log = get_logger("HostLinkBridge")

    def __init__(self, id, node_host, node_target, port_host, port_target, ip_host = None, mtu = "1500",
                 gateway_host = None, bridge_ns = "switch0"):
        check_not_null(id, "the id link cannot be null")
        check_not_null(port_host, "the port name host cannot be null")
        check_not_null(port_target, "the port name target cannot be null")
        super().__init__(type = LinkType.HOST, node_source = node_host, node_target = node_target)
        self._bridge_ns = bridge_ns
        self._ip_host = ip_host
        self._gateway_host = gateway_host
        self._mtu = mtu
        self._id = id

    def create(self):

        peer_src = rand_interface_name()
        peer_dst = rand_interface_name()
        link_bridge = "link{id}".format(id = self._id)

        try:

            IpRouteApi.create_pair(ifname = self.port_source, peer = peer_src, mtu = self._mtu)
            IpRouteApi.create_pair(ifname = self.port_target, peer = peer_dst, mtu = self._mtu)

            IpRouteApi.create_bridge(ifname = link_bridge, slaves = [peer_src, peer_dst], mtu = self._mtu)

            IpRouteApi.add_port_ns(ifname = self.port_source, netns = self.node_source)
            IpRouteApi.add_port_ns(ifname = self.port_target, netns = self.node_target)

            IpRouteApi.switch_on(ifname = self.port_source, netns = self.node_source)
            IpRouteApi.switch_on(ifname = self.port_target, netns = self.node_target)

            OvsdbApi.add_port_br(bridge = self._bridge_ns, netns = self.node_target, port_name = self.port_target)

            IpRouteApi.config_port_address(ifname = self.port_source, ip_addr = self._ip_host,
                                           gateway = self._gateway_host, netns = self.node_source)

        except Exception as ex:
            logger_host.error(str(ex.args))

    def delete(self, id):
        link_bridge = "link{id}".format(id = self._id)

        try:

            IpRouteApi.delete_port(ifname = self.port_source, netns = self.node_source)
            IpRouteApi.delete_port(ifname = self.port_target, netns = self.node_target)

            IpRouteApi.delete_port(ifname = link_bridge)

            OvsdbApi.del_port_br(bridge = self._bridge_ns, netns = self.node_target, port_name = self.port_target)

        except Exception as ex:
            logger_host.error(str(ex.args))
