from vsdnemul.link import Link, LinkType
from vsdnemul.log import get_logger
from vsdnemul.lib.ovsdblib import OvsdbApi
from vsdnemul.template.port import PortType
from vsdnemul.lib import check_not_null, disable_rx_off

logger = get_logger(__name__)


class DirectLinkOvs(Link):

    def __init__(self, node_source, node_target, bridge_ns = "switch0", mtu = "1500"):
        check_not_null(id, "the id link cannot be null")

        super().__init__(type = LinkType.DIRECT, node_source = node_source, node_target = node_target)
        self._bridge_ns = bridge_ns
        self._mtu = mtu

    def create(self):
        self.port_source = self.node_source.add_node_port(type = PortType.ETHERNET)
        self.port_target = self.node_target.add_node_port(type = PortType.ETHERNET)

        try:

            OvsdbApi.set_bridge(bridge = self.name)
            OvsdbApi.add_port_ns(bridge = self.name, netns = self.node_source.name, intf_name = self.port_source.name,
                                 mtu = self._mtu)
            OvsdbApi.add_port_ns(bridge = self.name, netns = self.node_target.name, intf_name = self.port_target.name,
                                 mtu = self._mtu)

            OvsdbApi.add_port_br(bridge = self._bridge_ns, port_name = self.port_source.name,
                                 netns = self.node_source.name)
            OvsdbApi.add_port_br(bridge = self._bridge_ns, port_name = self.port_target.name,
                                 netns = self.node_target.name)

            disable_rx_off(netns = self.node_source, port_name = self.port_source.name)
            disable_rx_off(netns = self.node_target, port_name = self.port_target.name)

            return self.node_source, self.node_target

        except Exception as ex:
            logger.error(str(ex.args[0]))

    def delete(self):

        try:

            OvsdbApi.del_port_br(bridge = self._bridge_ns, port_name = self.port_source.name,
                                 netns = self.node_source.name)
            OvsdbApi.del_port_br(bridge = self._bridge_ns, port_name = self.port_target.name,
                                 netns = self.node_target.name)

            OvsdbApi.del_port_ns(bridge = self.name, netns = self.node_source.name, intf_name = self.port_source.name)
            OvsdbApi.del_port_ns(bridge = self.name, netns = self.node_target.name, intf_name = self.port_target.name)

            OvsdbApi.del_bridge(bridge = self.name)

        except Exception as ex:
            logger.error(str(ex.args[0]))


class HostLinkOvs(Link):
    def __init__(self, node_host, node_target, ip_host, gateway_host = None, bridge_ns = "switch0", mtu = "1500"):

        super().__init__(type = LinkType.HOST, node_source = node_host, node_target = node_target)
        self._ip = check_not_null(ip_host, "the ip address cannot be null. eg: 192.168.0.1/24")
        self._gateway = gateway_host
        self._bridge_ns = bridge_ns
        self._mtu = mtu

    def create(self):

        self.port_source = self.node_source.add_node_port(type = PortType.ETHERNET)
        self.port_target = self.node_target.add_node_port(type = PortType.ETHERNET)

        try:

            OvsdbApi.set_bridge(bridge = self.name)

            OvsdbApi.add_port_ns(bridge = self.name, netns = self.node_source.name, intf_name = self.port_source.name,
                                 mtu = self._mtu, ip = self._ip, gateway = self._gateway)

            OvsdbApi.add_port_ns(bridge = self.name, netns = self.node_target.name, intf_name = self.port_target.name,
                                 mtu = self._mtu)

            OvsdbApi.add_port_br(bridge = self._bridge_ns, port_name = self.port_target.name,
                                 netns = self.node_target.name)

            disable_rx_off(netns = self.node_source, port_name = self.port_source.name)
            disable_rx_off(netns = self.node_target, port_name = self.port_target.name)

            return self.node_source, self.node_target

        except Exception as ex:
            logger.error(str(ex.args))

    def delete(self):

        try:

            OvsdbApi.del_port_ns(bridge = self.name, netns = self.node_source.name, intf_name = self.port_source.name)

            OvsdbApi.del_port_br(bridge = self._bridge_ns, port_name = self.port_target.name,
                                 netns = self.node_target.name)
            OvsdbApi.del_port_ns(bridge = self.name, netns = self.node_target.name, intf_name = self.port_target.name)

            OvsdbApi.del_bridge(bridge = self.name)

        except Exception as ex:
            logger.error(ex.args)
