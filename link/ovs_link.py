from api.link.linkapi import Link
from api.log.logapi import get_logger
from api.ovsdb.ovsdbapi import OvsdbApi
from api.utils import check_not_null

logger_direct = get_logger("DirectLinkOvs")


class DirectLinkOvs(Link):

    def __init__(self, node_source, node_target, bridge_ns = "switch0", mtu = "1500"):
        super().__init__(type = "direct-link-ovs", node_source = node_source, node_target = node_target, mtu = mtu)
        self._bridge_ns = bridge_ns

    def create(self):
        try:

            OvsdbApi.set_bridge(bridge = self.id)
            OvsdbApi.add_port_ns(bridge = self.id, netns = self.node_source, intf_name = self.port_source,
                                 mtu = self.mtu)
            OvsdbApi.add_port_ns(bridge = self.id, netns = self.node_target, intf_name = self.node_target,
                                 mtu = self.mtu)

            OvsdbApi.add_port_br(bridge = self._bridge_ns, port_name = self.port_source, netns = self.node_source)
            OvsdbApi.add_port_br(bridge = self._bridge_ns, port_name = self.port_target, netns = self.node_target)

        except Exception as ex:
            logger_direct.error(str(ex.args[0]))

    def delete(self):

        try:

            OvsdbApi.del_port_br(bridge = self._bridge_ns, port_name = self.port_source, netns = self.node_source)
            OvsdbApi.del_port_br(bridge = self._bridge_ns, port_name = self.port_target, netns = self.node_target)

            OvsdbApi.del_port_ns(bridge = self.id, netns = self.node_source, intf_name = self.port_source)
            OvsdbApi.del_port_ns(bridge = self.id, netns = self.node_target, intf_name = self.port_target)

            OvsdbApi.del_bridge(bridge = self.id)

        except Exception as ex:
            logger_direct.error(str(ex.args[0]))


logger_host = get_logger("HostLinkOvsVeth")


class HostLinkOvs(Link):
    def __init__(self, ip_host, gateway_host = None, node_host = None, node_target = None, bridge_ns = "switch0",
                 mtu = "1500"):
        super().__init__(type = "host-link-ovs", node_source = node_host, node_target = node_target, mtu = mtu)
        self._ip = check_not_null(ip_host, "the ip address cannot be null. eg: 192.168.0.1/24")
        self._gateway = gateway_host
        self._bridge_ns = bridge_ns

    def create(self):
        try:

            OvsdbApi.set_bridge(bridge = self.id)
            OvsdbApi.add_port_ns(bridge = self.id, netns = self.node_source, intf_name = self.port_source,
                                 mtu = self.mtu,ip = self._ip, gateway = self._gateway)

            OvsdbApi.add_port_ns(bridge = self.id, netns = self.node_target, intf_name = self.port_target,
                                 mtu = self.mtu)

            OvsdbApi.add_port_br(bridge = self._bridge_ns, port_name = self.port_target, netns = self.port_target)

        except Exception as ex:
            logger_host.error(str(ex.args))

    def delete(self):

        try:

            OvsdbApi.del_port_ns(bridge = self.id, netns = self.node_source, intf_name = self.port_source)

            OvsdbApi.del_port_br(bridge = self._bridge_ns, port_name = self.port_target, netns = self.node_target)
            OvsdbApi.del_port_ns(bridge = self.id, netns = self.node_target, intf_name = self.port_target)

            OvsdbApi.del_bridge(bridge = self.id)

        except Exception as ex:
            logger_host.error(ex.args)
