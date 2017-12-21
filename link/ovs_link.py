from api.link.linkapi import Link, LinkType
from api.log.logapi import get_logger
from api.ovsdb.ovsdbapi import OvsdbApi
from api.utils import check_not_null

logger_direct = get_logger("DirectLinkOvs")


class DirectLinkOvs(Link):

    def __init__(self, id, node_source, node_target, port_source, port_target, bridge_ns = "switch0", mtu = "1500"):
        check_not_null(id, "the id link cannot be null")
        check_not_null(port_source, "the port name source cannot be null")
        check_not_null(port_target, "the port name target cannot be null")

        super().__init__(description = "direct-link-ovs", type = LinkType.DIRECT,node_source = node_source,
                         node_target = node_target, port_target = port_target, port_source = port_source)
        self._bridge_ns = bridge_ns
        self._mtu = mtu
        self._id = id

    def create(self):
        link_bridge = "link{id}".format(id = self._id)

        try:

            OvsdbApi.set_bridge(bridge = link_bridge)
            OvsdbApi.add_port_ns(bridge = link_bridge, netns = self.node_source, intf_name = self.port_source,
                                 mtu = self._mtu)
            OvsdbApi.add_port_ns(bridge = link_bridge, netns = self.node_target, intf_name = self.port_target,
                                 mtu = self._mtu)

            OvsdbApi.add_port_br(bridge = self._bridge_ns, port_name = self.port_source, netns = self.node_source)
            OvsdbApi.add_port_br(bridge = self._bridge_ns, port_name = self.port_target, netns = self.node_target)

        except Exception as ex:
            logger_direct.error(str(ex.args[0]))

    def delete(self):

        link_bridge = "link{id}".format(id = self._id)

        try:

            OvsdbApi.del_port_br(bridge = self._bridge_ns, port_name = self.port_source, netns = self.node_source)
            OvsdbApi.del_port_br(bridge = self._bridge_ns, port_name = self.port_target, netns = self.node_target)

            OvsdbApi.del_port_ns(bridge = link_bridge, netns = self.node_source, intf_name = self.port_source)
            OvsdbApi.del_port_ns(bridge = link_bridge, netns = self.node_target, intf_name = self.port_target)

            OvsdbApi.del_bridge(bridge = link_bridge)

        except Exception as ex:
            logger_direct.error(str(ex.args[0]))


logger_host = get_logger("HostLinkOvsVeth")


class HostLinkOvs(Link):
    def __init__(self, id, node_host, node_target,port_host, port_target, ip_host, gateway_host = None,
                 bridge_ns = "switch0", mtu = "1500"):
        check_not_null(id, "the id link cannot be null")
        check_not_null(port_host, "the port name host cannot be null")
        check_not_null(port_target, "the port name target cannot be null")
        super().__init__(type = LinkType.HOST, port_source = port_host, port_target = port_target,
                         description = "host-link-ovs", node_source = node_host, node_target = node_target)
        self._ip = check_not_null(ip_host, "the ip address cannot be null. eg: 192.168.0.1/24")
        self._gateway = gateway_host
        self._bridge_ns = bridge_ns
        self._mtu = mtu
        self._id = id

    def create(self):
        try:

            OvsdbApi.set_bridge(bridge = self._id)

            OvsdbApi.add_port_ns(bridge = self._id, netns = self.node_source, intf_name = self.port_source,
                                 mtu = self._mtu, ip = self._ip, gateway = self._gateway)

            OvsdbApi.add_port_ns(bridge = self._id, netns = self.node_target, intf_name = self.port_target,
                                 mtu = self._mtu)

            OvsdbApi.add_port_br(bridge = self._bridge_ns, port_name = self.port_target, netns = self.node_target)

        except Exception as ex:
            logger_host.error(str(ex.args))

    def delete(self):

        try:

            OvsdbApi.del_port_ns(bridge = self._id, netns = self.node_source, intf_name = self.port_source)

            OvsdbApi.del_port_br(bridge = self._bridge_ns, port_name = self.port_target, netns = self.node_target)
            OvsdbApi.del_port_ns(bridge = self._id, netns = self.node_target, intf_name = self.port_target)

            OvsdbApi.del_bridge(bridge = self._id)

        except Exception as ex:
            logger_host.error(ex.args)
