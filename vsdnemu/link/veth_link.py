from vsdnemu.api.iproute.iprouteapi import IpRouteApi
from vsdnemu.api.link.linkapi import Link, LinkType
from vsdnemu.api.log.logapi import get_logger
from vsdnemu.api.ovsdb.ovsdbapi import OvsdbApi
from vsdnemu.api.port.portapi import PortType
from vsdnemu.api.utils.utils import rand_interface_name, check_not_null, disable_rx_off

logger = get_logger(__name__)


class DirectLinkVeth(Link):
    def __init__(self, node_source, node_target, bridge_ns = "switch0", mtu = "1500"):
        super().__init__(node_source = node_source, node_target = node_target, type = LinkType.DIRECT)
        self._bridge_ns = bridge_ns
        self._mtu = mtu

    def create(self):
        self.port_source = self.node_source.add_node_port(type = PortType.ETHERNET)
        self.port_target = self.node_target.add_node_port(type = PortType.ETHERNET)

        try:

            port_src = rand_interface_name()
            port_dst = rand_interface_name()

            IpRouteApi.create_pair(ifname = port_src, peer = port_dst, mtu = self._mtu)
            IpRouteApi.add_port_ns(ifname = port_src, netns = self.node_source.name, new_name = self.port_source.name)
            IpRouteApi.add_port_ns(ifname = port_dst, netns = self.node_target.name, new_name = self.port_target.name)
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
            IpRouteApi.delete_port(ifname = self.port_source.name, netns = self.node_source.name)
            OvsdbApi.del_port_br(bridge = self._bridge_ns, port_name = self.port_source.name,
                                 netns = self.node_source.name)
            OvsdbApi.del_port_br(bridge = self._bridge_ns, port_name = self.port_target.name,
                                 netns = self.node_target.name)

        except Exception as ex:
            logger.error(str(ex.args))


class HostLinkVeth(Link):

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

        try:
            port_src = rand_interface_name()
            port_dst = rand_interface_name()

            IpRouteApi.create_pair(ifname = port_src, peer = port_dst, mtu = self._mtu)
            IpRouteApi.add_port_ns(ifname = port_src, netns = self.node_source.name, new_name = self.port_source.name)
            IpRouteApi.add_port_ns(ifname = port_dst, netns = self.node_target.name, new_name = self.port_target.name)

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

    def delete(self):

        try:
            IpRouteApi.delete_port(ifname = self.port_source.name, netns = self.node_source.name)
            OvsdbApi.del_port_br(bridge = self._bridge_ns, netns = self.node_target.name,
                                 port_name = self.port_target.name)
        except Exception as ex:
            logger.error(str(ex.args))