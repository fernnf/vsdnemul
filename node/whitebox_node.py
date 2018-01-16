from api.docker.dockerapi import DockerApi
from api.log.logapi import get_logger
from api.node.nodeapi import Node, NodeType
from api.ovsdb.ovsdbapi import OvsdbApi

logger = get_logger("Whitebox")


class WhiteBox(Node):

    def __init__(self, name = None):

        super().__init__(name = name,
                         type = NodeType.SWITCH,
                         services = None,
                         image = "vsdn/whitebox",
                         volume = None,
                         cap_add = ["ALL"])

    def set_controller(self, ip = None, port = "6653", bridge = "switch0", type = "tcp"):
        try:
            OvsdbApi.set_controller(ip = ip, bridge = bridge, netns = self.name, type = type, port = port)
        except Exception as ex:
            logger.error(ex.args[0])

    def del_controller(self, bridge = "switch0"):
        try:
            OvsdbApi.del_bridge(bridge = bridge, netns = self.name)
        except Exception as ex:
            logger.error(ex.args[0])

    def set_manager(self, ip = None, port = "6640", type = "tcp"):
        try:
            OvsdbApi.set_manager(ip = ip, netns = self.name, port = port, type = type)
        except Exception as ex:
            logger.error(ex.args[0])

    def add_port(self, bridge = "switch0", port = None):
        try:
            OvsdbApi.add_port_br(bridge = bridge, port_name = port, netns = self.name)
        except Exception as ex:
            logger.error(ex.args[0])

    def del_port(self, bridge = "switch0", port = None):
        try:
            OvsdbApi.del_port_br(bridge = bridge, port_name = port, netns = self.name)
        except Exception as ex:
            logger.error(ex.args[0])

    def set_openflow_version(self, bridge = "switch0", version = "OpenFlow13"):
        try:
            OvsdbApi.change_openflow_version(netns = self.name, bridge = bridge, version = version)
        except Exception as ex:
            logger.error(ex.args[0])

    def set_bridge(self, bridge = None, dpid = None, version = "OpenFlow13", datapath_type = "netdev"):
        try:
            OvsdbApi.set_bridge(bridge = bridge, dpid = dpid, netns = self.name, of_ver = version,
                                dp_type = datapath_type)
        except Exception as ex:
            logger.error(ex.args[0])

    def rem_bridge(self, bridge = None):
        try:
            OvsdbApi.del_bridge(bridge = bridge, netns = self.name)
        except Exception as ex:
            logger.error(ex.args[0])

    def create(self):

        ret = DockerApi.create_node(name = self.name, image = self.image, ports = self.services,
                                    volumes = self.volume, cap_add = self.cap_add)
        if ret is not True:
            logger.error("the whitebox node cannot be created")

    def delete(self):
        ret = DockerApi.delete_node(name = self.name)

        if ret is not True:
            logger.error("the whitebox node cannot be deleted")
