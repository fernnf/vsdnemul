from api.link.linkapi import Link
from log import Logger
from api.ovsdb.ovsdbapi import OvsdbNode
from api.utils import check_not_null


class DirectLinkOvs(Link):
    logger = Logger.logger("DirectLinkOvs")

    def __init__(self, bridge_ns = "switch0", node_source = None, node_target = None):
        super().__init__(type = "direct-link-ovs", node_source = node_source, node_target = node_target)
        self._bridge_ns = bridge_ns

    def create(self):
        pid_src = self.node_source.node_pid
        pid_dst = self.node_target.node_pid
        if_src = self.port_source
        if_dst = self.port_target
        link_name = self.id

        try:

            OvsdbNode.set_bridge(bridge = link_name)
            OvsdbNode.add_port_ns(bridge = link_name, netns = pid_src, intf_name = if_src, mtu = 1500)
            OvsdbNode.add_port_ns(bridge = link_name, netns = pid_dst, intf_name = if_dst, mtu = 1500)

            OvsdbNode.add_port_br(bridge = self._bridge_ns, port_name = if_src, netns = pid_src)
            OvsdbNode.add_port_br(bridge = self._bridge_ns, port_name = if_dst, netns = pid_dst)

            self.node_source.add_port_br(port = self.port_source)
            self.node_target.add_port_br(port = self.port_target)

        except Exception as ex:
            self.logger.error(str(ex.args[0]))

    def delete(self):
        pid_src = self.node_source.node_pid
        pid_dst = self.node_target.node_pid
        if_src = self.port_source
        if_dst = self.port_target
        link_name = self.id

        try:
            OvsdbNode.del_port_ns(bridge = link_name, netns = pid_src, intf_name = if_src)
            OvsdbNode.del_port_ns(bridge = link_name, netns = pid_dst, intf_name = if_dst)
            OvsdbNode.del_bridge(bridge = link_name)

            OvsdbNode.rem_port_br(bridge = self._bridge_ns, port_name = if_src, netns = pid_src)
            OvsdbNode.rem_port_br(bridge = self._bridge_ns, port_name = if_dst, netns = pid_dst)

            self.node_source.del_port(port = self.port_source)
            self.node_target.del_port(port = self.port_target)
        except Exception as ex:
            self.logger.error(str(ex.args[0]))


class HostLinkOvs(Link):
    logger = Logger.logger("HostLinkOvsVeth")

    def __init__(self, ip_host, gateway_host = None, node_host = None, node_target = None, bridge_ns="switch0"):
        super().__init__(type = "host-link-ovs", node_source = node_host, node_target = node_target)
        self._ip = check_not_null(ip_host, "the ip address cannot be null. eg: 192.168.0.1/24")
        self._gateway = gateway_host
        self._bridge_ns = bridge_ns

    def create(self):
        pid_src = self.node_source.node_pid
        pid_dst = self.node_target.node_pid
        if_src = self.port_source
        if_dst = self.port_target
        link_name = self.id

        try:

            OvsdbNode.set_bridge(bridge = link_name)
            OvsdbNode.add_port_ns(bridge = link_name, netns = pid_src, intf_name = if_src, mtu = 1500, ip = self._ip,
                                  gateway = self._gateway)

            OvsdbNode.add_port_ns(bridge = link_name, netns = pid_dst, intf_name = if_dst, mtu = 1500)
            OvsdbNode.rem_port_br(bridge = self._bridge_ns, port_name = if_dst, netns = pid_dst)

            self.node_target.add_port_br(port = self.port_target)
        except Exception as ex:
            self.logger.error(str(ex.args))

    def delete(self):
        pid_src = self.node_source.node_pid
        pid_dst = self.node_target.node_pid
        if_src = self.port_source
        if_dst = self.port_target
        link_name = self.id
        try:

            OvsdbNode.del_port_ns(bridge = link_name, netns = pid_src, intf_name = if_src)
            OvsdbNode.del_port_ns(bridge = link_name, netns = pid_dst, intf_name = if_dst)
            OvsdbNode.del_bridge(bridge = link_name)

            OvsdbNode.rem_port_br(bridge = self._bridge_ns, port_name = if_dst, netns = pid_dst)

            self.node_target.del_port(port = self.port_target)
        except Exception as ex:
            self.logger.error(ex.args)


