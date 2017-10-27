import logging

import docker
import pyroute2

from functions import ApiNode
from utils import check_not_null, create_namespace, delete_namespace

_client_docker = docker.from_env()
_client_iproute = pyroute2.IPRoute()


# noinspection PyAttributeOutsideInit
class Node(object):
    logger = logging.getLogger("node.Node")

    def __init__(self, label = None, type = None, service = None, image = None):
        self.label = label
        self.type = type
        self.service = service
        self.image = image

    @property
    def image(self):
        return self.__image

    @image.setter
    def image(self, value):
        self.__image = check_not_null(value = value, msg = "the image name cannot be null")

    @property
    def label(self):
        return self.__name

    @label.setter
    def label(self, value):
        self.__image = check_not_null(value = value, msg = "the label node cannot be null")

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
        self.__type = check_not_null(value = value, msg = "the type node cannot be null")

    @property
    def control_ip(self):
        try:
            return ApiNode.has_node_ip_management(label = self.label)
        except Exception as ex:
            print("Error: {error}".format(error = ex.args[0]))

    @property
    def service_exposed_port(self, service_port = None):
        try:
            return ApiNode.has_node_service_exposed_port(label = self.label, service_port = service_port)
        except Exception as ex:
            print("Error: {error}".format(error = ex.args[0]))

    @property
    def node_pid(self):
        try:
            return ApiNode.has_node_pid(label = self.label)
        except Exception as ex:
            print("Error: {error}".format(error = ex.args[0]))

    @property
    def node_status(self):
        try:
            return ApiNode.node_status(label = self.label)
        except Exception as ex:
            print("Error: {error}".format(error = ex.args[0]))

    def send_cmd(self, cmd = None):
        try:
            return ApiNode.node_send_cmd(self.label, cmd = cmd)
        except Exception as ex:
            print("Error: {error}".format(error = ex.args[0]))


class WhiteBox(Node):
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
            print("Error: {error}".format(error = ex.args[0]))

    def del_controller(self, bridge = "switch0"):
        try:
            ApiWhiteboxOVS.service_del_bridge_controller(label = self.label, bridge_name = bridge)
        except Exception as ex:
            print("Error: {error}".format(error = ex.args[0]))

    def set_manager(self, ip = None, port = "6640", type = "tcp"):
        try:
            ApiWhiteboxOVS.service_set_ovs_manager(label = self.label, ip = ip, service_port = port, type = type)
        except Exception as ex:
            print("Error: {error}".format(error = ex.args[0]))

    def add_port(self, bridge = "switch0", port = None):
        try:
            ApiWhiteboxOVS.service_add_port(label = self.label, bridge = bridge, port_name = port)
        except Exception as ex:
            print("Error: {error}".format(error = ex.args[0]))

    def del_port(self, bridge = "switch0", port = None):
        try:
            ApiWhiteboxOVS.service_del_port(label = self.label, bridge = bridge, port_name = port);
        except Exception as ex:
            print("Error: {error}".format(error = ex.args[0]))

    def set_openflow_version(self, bridge = "switch0", version = "OpenFlow13"):
        try:
            ApiWhiteboxOVS.service_set_openflow_ver(label = self.label, bridge = bridge, version = version)
        except Exception as ex:
            print("Error: {error}".format(error = ex.args[0]))

    def set_bridge(self, bridge = None, dpid = None, version = "OpenFlow13", datapath_type = "netdev"):
        try:
            ApiWhiteboxOVS.service_set_bridge(label = self.label, bridge = bridge, dpid = dpid, version = version,
                                              datapath_type = datapath_type)
        except Exception as ex:
            print("Error: {error}".format(error = ex.args[0]))

    def rem_bridge(self, bridge = None):
        try:
            ApiWhiteboxOVS.service_rem_bridge(label = self.label, bridge = bridge)
        except Exception as ex:
            print("Error: {error}".format(error = ex.args[0]))

    def create(self):
        try:
            return ApiNode.create_node(label = self.label, image = self.image, service = self.service)
        except Exception as ex:
            print("Error: A error occurred on create of node {error}".format(error = ex.args[0]))

    def delete(self):
        try:
            return ApiNode.delete_node(label = self.label)
        except Exception as ex:
            print("Error: A error occurred on delete of node {error}".format(error = ex.args[0]))


class Host(Node):
    def __init__(self, label = None):
        super().__init__(label = label, type = "vsdn/host", service = {'22/tcp': None})


class ApiNode(object):
    @staticmethod
    def create_node(label, image, service):
        _client_docker.containers \
            .run(image = image,
                 hostname = label,
                 name = label,
                 ports = service,
                 detach = True,
                 tty = True,
                 stdin_open = True,
                 privileged = True)
        status = ApiNode.node_status(label = label)

        if status == "running":
            pid = ApiNode.has_node_pid(label = label)
            create_namespace(pid = pid)
            return True
        else:
            return False

    @staticmethod
    def delete_node(label):
        container = _client_docker.containers.get(label)
        delete_namespace(ApiNode.has_node_pid(label = label))
        container.stop()
        container.remove()

    @staticmethod
    def node_pause(label):
        container = _client_docker.containers.get(label)
        container.pause()

    @staticmethod
    def node_resume(label):
        container = _client_docker.containers.get(label)
        container.unpause()

    @staticmethod
    def node_status(label):
        container = _client_docker.containers.get(label)
        return container.status

    @staticmethod
    def has_node_pid(label):
        container = _client_docker.containers.get(label)
        return container.attrs["State"]["Pid"]

    @staticmethod
    def has_node_ip_management(label):
        container = _client_docker.containers.get(label)
        return container.attrs['NetworkSettings']['IPAddress']

    @staticmethod
    def has_node_service_exposed_port(label, service_port):
        container = _client_docker.containers.get(label)
        return container.attrs['NetworkSettings']['Ports'][service_port + "/tcp"][0]['HostPort']

    @staticmethod
    def node_send_cmd(label, cmd):
        container = _client_docker.containers.get(label)
        ret = container.exec_run(cmd = cmd, tty = True, privileged = True)
        return ret


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


class NodeGroup(object):
    def __init__(self):
        self.__nodes = {}

    def add_node(self, node):
        self.__nodes = self.__nodes + {node.label: node}

    def rem_node(self, node):
        del self.__nodes[node.label]

    def get_nodes(self):
        return self.__nodes.copy()

    def get_node(self, label):
        return self.__nodes[label]

    def commit(self):
        if len(self.__nodes) <= 0:
            raise RuntimeError("there is not node to commit")
        else:
            for k, v in self.__nodes.items():
                print("creating node ({label})".format(label = k), )
                v.create()

    def remove(self):
        if len(self.__nodes) <= 0:
            raise RuntimeError("there is not node to commit")
        else:
            for k, v in self.__nodes.items():
                print("removing node ({label})".format(label = k), )
                v.delete()
