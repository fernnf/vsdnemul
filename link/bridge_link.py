from api.iproute.iprouteapi import IpRouteApi
from api.link.linkapi import Link
from api.log.logapi import get_logger
from api.ovsdb.ovsdbapi import OvsdbApi

logger_direct = get_logger("DirectLinkBridge")


class DirectLinkBridge(Link):

    def __init__(self, node_source, node_target, bridge_ns = "switch0", mtu = "1500"):
        super().__init__(type = "direct-link-bridge", node_source = node_source, node_target = node_target, mtu = mtu)
        self._bridge_ns = bridge_ns

    def create(self):

        if_src = self.node_source + "_" + self.node_target
        peer_src = self.node_source + "_" + self.id
        if_dst = self.node_target + "_" + self.node_source
        peer_dst = self.node_target + "_" + self.id

        try:
            IpRouteApi.create_bridge(ifname = self.id)

            IpRouteApi.create_pair(ifname = if_src, peer = peer_src, mtu = self.mtu)
            IpRouteApi.create_pair(ifname = if_dst, peer = peer_dst, mtu = self.mtu)

            IpRouteApi.add_port_ns(ifname = if_src, netns = self.node_source)
            IpRouteApi.add_port_ns(ifname = if_dst, netns = self.node_target)

            IpRouteApi.switch_on(ifname = if_src, netns = self.node_source)
            IpRouteApi.switch_on(ifname = if_dst, netns = self.node_target)

            IpRouteApi.bridge_add_port(master = self.id, slaves = [peer_src, peer_dst])

            OvsdbApi.add_port_br(bridge = self._bridge_ns, netns = self.node_source, port_name = if_src)
            OvsdbApi.add_port_br(bridge = self._bridge_ns, netns = self.node_target, port_name = if_dst)

        except Exception as ex:
            logger_direct.error(str(ex.args))

    def delete(self):

        if_src = self.node_source + "_" + self.node_target
        if_dst = self.node_target + "_" + self.node_source

        try:
            IpRouteApi.delete_port(ifname = if_src, netns = self.node_source)
            IpRouteApi.delete_port(ifname = if_dst, netns = self.node_target)

            IpRouteApi.delete_port(ifname = self.id)

            OvsdbApi.del_port_br(bridge = self._bridge_ns, port_name = if_src, netns = self.node_source)
            OvsdbApi.del_port_br(bridge = self._bridge_ns, port_name = if_dst, netns = self.node_target)

        except Exception as ex:
            logger_direct.error(str(ex.args))


logger_host = get_logger("HostLinkBridge")


class HostLinkBridge(Link):
    log = get_logger("HostLinkBridge")

    def __init__(self, ip_host, mtu = "1500", gateway_host = None, bridge_ns = "switch0", node_source = None,
                 node_target = None):
        super().__init__(type = "host-link-bridge", node_source = node_source, node_target = node_target)
        self._bridge_ns = bridge_ns
        self._ip_host = ip_host
        self._gateway_host = gateway_host
        self._mtu = mtu

    def create(self):

        if_src = self.node_source + "_" + self.node_target
        peer_src = self.node_source + "_" + self.id
        if_dst = self.node_target + "_" + self.node_source
        peer_dst = self.node_target + "_" + self.id

        try:

            IpRouteApi.create_pair(ifname = if_src, peer = peer_src, mtu = self.mtu)
            IpRouteApi.create_pair(ifname = if_dst, peer = peer_dst, mtu = self.mtu)

            IpRouteApi.create_bridge(ifname = self.id, slaves = [peer_src, peer_dst], mtu = self.mtu)

            IpRouteApi.add_port_ns(ifname = if_src, netns = self.node_source)
            IpRouteApi.add_port_ns(ifname = if_dst, netns = self.node_target)

            IpRouteApi.switch_on(ifname = if_src, netns = self.node_source)
            IpRouteApi.switch_on(ifname = if_dst, netns = self.node_target)

            OvsdbApi.add_port_br(bridge = self._bridge_ns, netns = self.node_target, port_name = if_dst)

            IpRouteApi.config_port_address(ifname = if_src, ip_addr = self._ip_host, gateway = self._gateway_host,
                                           netns = self.node_source)

        except Exception as ex:
            logger_host.error(str(ex.args))

    def delete(self):
        if_src = self.node_source + "_" + self.node_target
        if_dst = self.node_target + "_" + self.node_source

        try:

            IpRouteApi.delete_port(ifname = if_src, netns = self.node_source)
            IpRouteApi.delete_port(ifname = if_dst, netns = self.node_target)

            IpRouteApi.delete_port(ifname = self.id)

            OvsdbApi.del_port_br(bridge = self._bridge_ns, netns = self.node_target, port_name = if_dst)

        except Exception as ex:
            logger_host.error(str(ex.args))
