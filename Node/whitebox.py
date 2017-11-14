from log import Logger
from Node.node import Node, ApiNode
from utils import check_not_null


class WhiteBox(Node):
    logger = Logger.logger("WhiteBox")

    def __init__(self, label = None):
        super().__init__(label = label,
                         type = "WhiteBox",
                         service = {'22/tcp': None, '6633/tcp': None, '6640/tcp': None, '6653/tcp': None},
                         image = "vsdn/whitebox")

    def set_controller(self, ip = None, port = "6653", bridge = "switch0", type = "tcp"):
        try:
            ApiWhiteboxOVS.service_set_bridge_controller(label = self.label, bridge_name = bridge, ip = ip,
                                                         service_port = port, type = type)
        except Exception as ex:
            self.logger.error(ex.args[0])

    def del_controller(self, bridge = "switch0"):
        try:
            ApiWhiteboxOVS.service_del_bridge_controller(label = self.label, bridge_name = bridge)
        except Exception as ex:
            self.logger.error(ex.args[0])

    def set_manager(self, ip = None, port = "6640", type = "tcp"):
        try:
            ApiWhiteboxOVS.service_set_ovs_manager(label = self.label, ip = ip, service_port = port, type = type)
        except Exception as ex:
            self.logger.error(ex.args[0])

    def add_port(self, bridge = "switch0", port = None):
        try:
            ApiWhiteboxOVS.service_add_port(label = self.label, bridge = bridge, port_name = port)
        except Exception as ex:
            self.logger.error(ex.args[0])

    def del_port(self, bridge = "switch0", port = None):
        try:
            ApiWhiteboxOVS.service_del_port(label = self.label, bridge = bridge, port_name = port);
        except Exception as ex:
            self.logger.error(ex.args[0])

    def set_openflow_version(self, bridge = "switch0", version = "OpenFlow13"):
        try:
            ApiWhiteboxOVS.service_set_openflow_ver(label = self.label, bridge = bridge, version = version)
        except Exception as ex:
            self.logger.error(ex.args[0])

    def set_bridge(self, bridge = None, dpid = None, version = "OpenFlow13", datapath_type = "netdev"):
        try:
            ApiWhiteboxOVS.service_set_bridge(label = self.label, bridge = bridge, dpid = dpid, version = version,
                                              datapath_type = datapath_type)
        except Exception as ex:
            self.logger.error(ex.args[0])

    def rem_bridge(self, bridge = None):
        try:
            ApiWhiteboxOVS.service_rem_bridge(label = self.label, bridge = bridge)
        except Exception as ex:
            self.logger.error(ex.args[0])

    def create(self):
        try:
            return ApiNode.create_node(label = self.label, image = self.image, service = self.service)
        except Exception as ex:
            self.logger.error(ex.args[0])

    def delete(self):
        try:
            return ApiNode.delete_node(label = self.label)
        except Exception as ex:
            self.logger.error(str(ex.args))


class ApiWhiteboxOVS(object):
    @staticmethod
    def service_set_bridge_controller(label = None, ip = None, service_port = "6653", bridge_name = "switch0",
                                      type = "tcp"):
        check_not_null(label, "The label cannot be null")
        check_not_null(ip, "the ip cannot be null")

        cmd_set_controller = "ovs-vsctl set-controller {bridge} {type}:{ip}:{port}" \
            .format(ip = ip, bridge = bridge_name, type = type, port = service_port)

        ret = ApiNode.node_send_cmd(label = label, cmd = cmd_set_controller)

        if len(ret) != 0:
            raise ValueError(ret.decode)

    @staticmethod
    def service_del_bridge_controller(label = None, bridge_name = "swtich0"):
        check_not_null(label, "the label cannot be null")

        cmd_del_controller = "ovs-vsctl del-controller {bridge}".format(bridge = bridge_name)

        ret = ApiNode.node_send_cmd(label = label, cmd = cmd_del_controller)

        if len(ret) != 0:
            raise ValueError(ret.decode)

    @staticmethod
    def service_set_ovs_manager(label = None, ip = None, service_port = "6640", type = "tcp"):
        check_not_null(label, "The label cannot be null")
        check_not_null(ip, "the ip cannot be null")

        cmd_set_manager = "ovs-vsctl set-manager {type}:{port}".format(type = type, port = service_port)
        ret = ApiNode.node_send_cmd(label = label, cmd = cmd_set_manager)

        if len(ret) != 0:
            raise ValueError(ret.decode())

    @staticmethod
    def service_del_ovs_manager(label = None):
        check_not_null(label, "the label cannot be null")

        cmd_del_manager = "ovs-vsctl del-manager"
        ret = ApiNode.node_send_cmd(label = label, cmd = cmd_del_manager)

        if len(ret) != 0:
            raise ValueError(ret.decode())

    @staticmethod
    def service_add_port(label = None, bridge = "switch0", port_name = None):
        check_not_null(value = label, msg = "the label cannot be null")
        check_not_null(value = port_name, msg = "the port name cannot be null")

        cmd_add_interface = "ovs-vsctl add-port {bridge} {port} -- set Interface {port} type=system" \
            .format(bridge = bridge, port = port_name)

        ret = ApiNode.node_send_cmd(label = label, cmd = cmd_add_interface)

        if len(ret) != 0:
            raise ValueError(ret.decode())

    @staticmethod
    def service_del_port(label = None, bridge = "switch0", port_name = None):
        check_not_null(value = label, msg = "the label cannot be null")
        check_not_null(value = port_name, msg = "the port name cannot be null")

        cmd_del_interface = "ovs-vsctl del-port {bridge} {port}".format(bridge = bridge, port = port_name)

        ret = ApiNode.node_send_cmd(label = label, cmd = cmd_del_interface)

        if len(ret) != 0:
            raise ValueError(ret.decode())

    @staticmethod
    def service_set_openflow_ver(label = None, bridge = "switch0", version = "OpenFlow13"):
        check_not_null(value = label, msg = "the label cannot be null")

        cmd_set_protocols = "ovs-vsctl set bridge {bridge} protocols={version}" \
            .format(bridge = bridge, version = version)

        ret = ApiNode.node_send_cmd(label = label, cmd = cmd_set_protocols)

        if len(ret) != 0:
            raise ValueError(ret.decode())

    @staticmethod
    def service_set_bridge(label = None, bridge = None, dpid = None, version = "OpenFlow13", datapath_type = "netdev"):
        check_not_null(value = label, msg = "the label cannot be null")
        check_not_null(value = bridge, msg = "the bridge name cannot be null")

        cmd_set_bridge = "ovs-vsctl add-br {bridge} -- set bridge {bridge} datapath_type={dp_type} protocols={version}" \
            .format(bridge = bridge, dp_type = datapath_type, version = version)

        if dpid is not None:
            cmd_set_bridge = cmd_set_bridge + " other_config:datapath_id={dpid}".format(dpid = dpid)

        ret = ApiNode.node_send_cmd(label = label, cmd = cmd_set_bridge)

        if len(ret) != 0:
            raise ValueError(ret.decode())

    @staticmethod
    def service_rem_bridge(label = None, bridge = None):
        check_not_null(value = label, msg = "the label cannot be null")
        check_not_null(value = bridge, msg = "the bridge name cannot be null")

        cmd_del_bridge = "ovs-vsctl del-br {bridge}".format(bridge = bridge)

        ret = ApiNode.node_send_cmd(label = label, cmd = cmd_del_bridge)

        if len(ret) != 0:
            raise ValueError(ret.decode())
