from vsdnemul.lib.iproute import IpRouteApi
from vsdnemul.link import Link, LinkType
from vsdnemul.lib.log import get_logger
from vsdnemul.lib.ovsdblib import OvsdbApi
from vsdnemul.models.port import PortType
from vsdnemul.lib import rand_interface_name, check_not_null, disable_rx_off

logger = get_logger(__name__)


class DirectLinkBridge(Link):

    def __init__(self, node_source, node_target, bridge_ns = "switch0", mtu = "1500"):

        super().__init__(index= None, node_source = node_source, node_target = node_target, type = LinkType.DIRECT)
        self._bridge_ns = bridge_ns
        self._mtu = mtu

    def create(self):

        self.port_source = self.node_source.add_node_port(type = PortType.ETHERNET)
        self.port_target = self.node_target.add_node_port(type = PortType.ETHERNET)

        peer_src = rand_interface_name()
        peer_dst = rand_interface_name()

        try:

            IpRouteApi.create_pair(ifname = self.port_source.name, peer = peer_src, mtu = self._mtu)
            IpRouteApi.create_pair(ifname = self.port_target.name, peer = peer_dst, mtu = self._mtu)
            IpRouteApi.create_bridge(ifname = self.name, slaves = [peer_src, peer_dst], mtu = self._mtu)
            IpRouteApi.add_port_ns(ifname = self.port_source.name, netns = self.node_source.name)
            IpRouteApi.add_port_ns(ifname = self.port_target.name, netns = self.node_target.name)
            IpRouteApi.switch_on(ifname = self.port_source.name, netns = self.node_source.name)
            IpRouteApi.switch_on(ifname = self.port_target.name, netns = self.node_target.name)
            OvsdbApi.add_port_br(bridge = self._bridge_ns, netns = self.node_source.name,
                                 port_name = self.port_source.name)
            OvsdbApi.add_port_br(bridge = self._bridge_ns, netns = self.node_target.name,
                                 port_name = self.port_target.name)

            disable_rx_off(netns = self.node_source, port_name = self.port_source.name)
            disable_rx_off(netns = self.node_target, port_name = self.port_target.name)

            return self.node_source, self.node_target

        except Exception as ex:
            logger.error(str(ex.args))

    def delete(self):

        try:
            IpRouteApi.delete_port(ifname = self.port_source.name, netns = self.node_source)
            IpRouteApi.delete_port(ifname = self.port_target.name, netns = self.node_target)
            OvsdbApi.del_port_br(bridge = self._bridge_ns, port_name = self.port_source, netns = self.node_source)
            OvsdbApi.del_port_br(bridge = self._bridge_ns, port_name = self.port_target, netns = self.node_target)
            IpRouteApi.delete_port(ifname = self.name)

        except Exception as ex:
            logger.error(str(ex.args))


class HostLinkBridge(Link):

    def __init__(self, node_host, node_target, ip_host = None, mtu = "1500", gateway_host = None,
                 bridge_ns = "switch0"):
        check_not_null(id, "the id link cannot be null")
        super().__init__(type = LinkType.HOST, node_source = node_host, node_target = node_target)
        self._bridge_ns = bridge_ns
        self._ip_host = ip_host
        self._gateway_host = gateway_host
        self._mtu = mtu

    def create(self):

        self.port_source = self.node_source.add_node_port(type = PortType.ETHERNET)
        self.port_target = self.node_target.add_node_port(type = PortType.ETHERNET)

        peer_src = rand_interface_name()
        peer_dst = rand_interface_name()

        try:

            IpRouteApi.create_pair(ifname = self.port_source.name, peer = peer_src, mtu = self._mtu)
            IpRouteApi.add_port_ns(ifname = self.port_source.name, netns = self.node_source.name)
            IpRouteApi.create_pair(ifname = self.port_target.name, peer = peer_dst, mtu = self._mtu)
            IpRouteApi.add_port_ns(ifname = self.port_target.name, netns = self.node_target.name)

            IpRouteApi.create_bridge(ifname = self.name, slaves = [peer_src, peer_dst], mtu = self._mtu)

            IpRouteApi.switch_on(ifname = self.port_source.name, netns = self.node_source.name)
            IpRouteApi.switch_on(ifname = self.port_target.name, netns = self.node_target.name)

            OvsdbApi.add_port_br(bridge = self._bridge_ns, netns = self.node_target.name,
                                 port_name = self.port_target.name)

            IpRouteApi.config_port_address(ifname = self.port_source.name, ip_addr = self._ip_host,
                                           gateway = self._gateway_host, netns = self.node_source.name)

            disable_rx_off(netns = self.node_source, port_name = self.port_source.name)
            disable_rx_off(netns = self.node_target, port_name = self.port_target.name)

            return self.node_source, self.node_target
        except Exception as ex:
            logger.error(str(ex.args))

    def delete(self, ):

        try:
            IpRouteApi.delete_port(ifname = self.port_source.name, netns = self.node_source.name)
            IpRouteApi.delete_port(ifname = self.port_target.name, netns = self.node_target.name)
            IpRouteApi.delete_port(ifname = self.name)
            OvsdbApi.del_port_br(bridge = self._bridge_ns, netns = self.node_target.name,
                                 port_name = self.port_target.name)

        except Exception as ex:
            logger.error(str(ex.args))
