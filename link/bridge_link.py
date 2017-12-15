from api.iproute.iprouteapi import IpRouteApi
from api.link.linkapi import Link
from api.log.logapi import get_logger
from api.ovsdb.ovsdbapi import OvsdbApi

logger_direct = get_logger("DirectLinkBridge")


class DirectLinkBridge(Link):

    def __init__(self, node_source, node_target, bridge_ns = "switch0", ):
        super().__init__(type = "direct-link-bridge", node_source = node_source, node_target = node_target)
        self._bridge_ns = bridge_ns

    def create(self):
        pid_src = self.node_source.node_pid
        pid_dst = self.node_target.node_pid

        if_src = self.port_source
        peer_src = self.node_source.name + "-" + self.id
        if_dst = self.port_target
        peer_dst = self.node_target.name + "-" + self.id

        link_name = self.id

        try:
            IpRouteApi.create_bridge(ifname = link_name)

            IpRouteApi.create_pair(ifname = if_src, peer = peer_src, mtu = 1500)
            IpRouteApi.create_pair(ifname = if_dst, peer = peer_dst, mtu = 1500)

            IpRouteApi.add_port_ns(ifname = if_src, netns = pid_src)
            IpRouteApi.add_port_ns(ifname = if_dst, netns = pid_dst)

            IpRouteApi.bridge_add_port(master = link_name, slaves = [peer_src, peer_src])

            OvsdbApi.add_port_br(bridge = self._bridge_ns, netns = pid_src, port_name = if_src)
            OvsdbApi.add_port_br(bridge = self._bridge_ns, netns = pid_dst, port_name = if_dst)

        except Exception as ex:
            logger_direct.error(str(ex.args[0]))

    def delete(self):

        pid_src = self.node_source.node_pid
        pid_dst = self.node_target.node_pid
        if_src = self.port_source
        if_dst = self.port_target
        link_name = self.id

        try:
            OvsdbApi.rem_port_br(bridge = link_name, port_name = if_src, netns = pid_src)
            OvsdbApi.rem_port_br(bridge = link_name, port_name = if_dst, netns = pid_dst)

            IpRouteApi.delete_port(ifname = if_src, netns = pid_src)
            IpRouteApi.delete_port(ifname = if_dst, netns = pid_dst)

            IpRouteApi.delete_port(ifname = link_name)

        except Exception as ex:
            logger_direct.error(str(ex.args[0]))


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
        pid_src = self.node_source.node_pid
        pid_dst = self.node_target.node_pid

        if_src = self.port_source
        peer_src = self.node_source.name + "-" + self.id
        if_dst = self.port_target
        peer_dst = self.node_target.name + "-" + self.id

        link_name = self.id

        try:
            IpRouteApi.create_bridge(ifname = link_name)

            IpRouteApi.create_pair(ifname = if_src, peer = peer_src, mtu = 1500)
            IpRouteApi.create_pair(ifname = if_dst, peer = peer_dst, mtu = 1500)

            IpRouteApi.add_port_ns(ifname = if_src, netns = pid_src)
            IpRouteApi.add_port_ns(ifname = if_dst, netns = pid_dst)

            IpRouteApi.bridge_add_port(master = link_name, slaves = [peer_src, peer_src])

            OvsdbApi.add_port_br(bridge = self._bridge_ns, netns = pid_dst, port_name = if_dst)

            IpRouteApi.config_port_address(ifname = if_src, ip_addr = self._ip_host, gateway = self._gateway,
                                           netns = pid_src)

        except Exception as ex:
            logger_host.error(str(ex.args[0]))
