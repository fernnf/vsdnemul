from Link.link import Link
from log import Logger
from utils import create_veth_link_containers, delete_veth_link_containers, config_interface_address, check_not_null


class DirectLinkOvsVeth(Link):
    logger = Logger.logger("DirectLinkOvsVeth")

    def __init__(self, node_source = None, node_target = None):
        super().__init__(type = "direct-link-ovs-veth", node_source = node_source, node_target = node_target)

    def create(self):
        pid_src = self.node_source.node_pid
        pid_dst = self.node_target.node_pid
        if_src = self.node_source.label
        if_dst = self.node_target.label
        link_name = self.id

        try:
            create_veth_link_containers(src_pid = pid_src, tgt_pid = pid_dst, src_name = if_src, tgt_name = if_dst,
                                        link_name = link_name)
            self.node_source.add_port(port = self.port_source)
            self.node_target.add_port(port = self.port_target)
        except Exception as ex:
            self.logger.error(str(ex.args[0]))

    def delete(self):
        if_src = self.node_source.label
        if_dst = self.node_target.label
        link_name = self.id

        try:
            delete_veth_link_containers(src_name = if_src, tgt_name = if_dst,link_name = link_name)
            self.node_source.del_port(port = self.port_source)
            self.node_target.del_port(port = self.port_target)
        except Exception as ex:
            self.logger.error(str(ex.args[0]))


class HostLinkOvsVeth(Link):
    logger = Logger.logger("HostLinkOvsVeth")

    def __init__(self, node_host = None, node_target = None, ip = None):
        super().__init__(type = "host-link-ovs-veth", node_source = node_host, node_target = node_target)
        self._ip = check_not_null(ip, "the ip address cannot be null. eg: 192.168.0.1/24")

    def create(self):
        pid_src = self.node_source.node_pid
        pid_dst = self.node_target.node_pid
        if_src = self.node_source.label
        if_dst = self.node_target.label
        link_name = self.id

        try:
            create_veth_link_containers(src_pid = pid_src, tgt_pid = pid_dst, src_name = if_src, tgt_name = if_dst,
                                        link_name = link_name)
            config_interface_address(pid = pid_src, if_name = self.port_source, addr = self._ip)
            self.node_target.add_port(port = self.port_target)
        except Exception as ex:
            self.logger.error(str(ex.args))

    def delete(self):
        if_src = self.port_source
        if_dst = self.port_target
        link_name = self.id
        try:

            delete_veth_link_containers(src_name = if_src, tgt_name = if_dst,link_name = link_name)
            self.node_target.del_port(port = self.port_target)
        except Exception as ex:
            self.logger.error(ex.args)
