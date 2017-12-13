from api.link.linkapi import Link
from api.iproute.iprouteapi import IpRouteApi
from api.ovsdb.ovsdbapi import OvsdbNode
from api.log.logapi import get_logger
from api.node.nodeapi import Node


class DirectLinkBridge(Link):

    def __init__(self, node_source: Node, node_target: Node, bridge_ns = "switch0",):
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

            OvsdbNode.add_port_br(bridge = self._bridge_ns, netns = pid_src, port_name = if_src)
            OvsdbNode.add_port_br(bridge = self._bridge_ns, netns = pid_dst, port_name = if_dst)

        except Exception as ex:
            self.logger.error(str(ex.args[0]))

    def delete(self):

        pid_src = self.node_source.node_pid
        pid_dst = self.node_target.node_pid
        if_src = self.port_source
        if_dst = self.port_target
        link_name = self.id

        try:
            OvsdbNode.rem_port_br(bridge = link_name, port_name = if_src, netns = pid_src)
            OvsdbNode.rem_port_br(bridge = link_name, port_name = if_dst, netns = pid_dst)

            IpRouteApi.delete_port(ifname = if_src, netns = pid_src)
            IpRouteApi.delete_port(ifname = if_dst, netns = pid_dst)

            IpRouteApi.delete_port(ifname = link_name)

        except Exception as ex:
            self.logger.error(str(ex.args[0]))


class HostLinkBridge(Link):

    log = get_logger("HostLinkBridge")

    def __init__(self, ip_addr, gateway = None, bridge_ns = "switch0", node_source = None, node_target = None):
        super().__init__(type = "host-link-bridge", node_source = node_source, node_target = node_target)
        self._bridge_ns = bridge_ns
        self._ip_addr = ip_addr
        self._gateway = gateway


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

            OvsdbNode.add_port_br(bridge = self._bridge_ns, netns = pid_dst, port_name = if_dst)

            IpRouteApi.config_port_address(ifname = if_src, ip_addr = self._ip_addr, gateway = self._gateway,
                                           netns = pid_src)

        except Exception as ex:
            self.log.error(str(ex.args[0]))
