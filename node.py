import logging
from enum import Enum, unique

import docker


@unique
class NodeType(Enum):
    Node = ""
    WhiteBox = "sdnoverlay/whitebox"


class Node(object):
    def __init__(self, name = "", node_type = NodeType.Node):
        self.name = name
        self.type = node_type

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        if name is not None:
            self.__name = name
        else:
            raise ValueError("The name node cannot be null")

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, node_type = NodeType.Node):

        if node_type in NodeType:
            print(node_type.name)
            self.__type = node_type
        else:
            raise ValueError("the type name is not valid")


class WhiteBoxNode(Node):
    def __init__(self, name = "", node_type = NodeType.WhiteBox):
        super().__init__(name = name, node_type = node_type)

    @property
    def bridge_oper(self):
        return "switch0"

    @bridge_oper.setter
    def bridge_oper(self, value):
        pass

    @property
    def openflow_ver(self):
        return "OpenFlow13"

    @openflow_ver.setter
    def openflow_ver(self, value):
        pass

    @property
    def volume_oper(self):
        return {'/sys/fs/cgroup': {'bind': '/sys/fs/cgroup', 'mode': 'ro'}}

    @volume_oper.setter
    def volume_oper(self, value):
        pass

    @property
    def service_port_opr(self):
        return {'22/tcp': None, '6633/tcp': None, '6640/tcp': None, '6653/tcp': None}

    @service_port_opr.setter
    def service_port_opr(self, value):
        pass


class WhiteBoxCommand(object):
    def __init__(self, node = WhiteBoxNode()):
        self.node = node
        self.logger = logging.getLogger("WhiteBoxCommand")

    @property
    def node(self):
        return self.__node

    @node.setter
    def node(self, node = WhiteBoxNode()):
        if isinstance(node, WhiteBoxNode):
            self.__node = node
        else:
            raise ReferenceError("the node must be instance of whiteboxnode")

    @classmethod
    def add_node(cls, node = WhiteBoxNode()):
        n = cls(node = node)

        try:
            n._commit()
            n._create_bridge()
        except Exception as e:
            n.logger.error(e.args)

    @classmethod
    def del_node(cls, node = WhiteBoxNode()):
        n = cls(node = node)
        try:
            n._remove()
        except Exception as e:
            n.logger.error(e.args)

    @classmethod
    def send_cmd(cls, node = WhiteBoxNode(), cmd = ""):
        n = cls(node = node)
        try:
            n._exec(cmd = cmd)
        except Exception as e:
            n.logger.error(e.args)

    @classmethod
    def add_port(cls, node = WhiteBoxNode(), port_name = "", port_idx = ""):
        n = cls(node = node)
        try:
            n._add_port(port_name = port_name, idx = port_idx)
        except Exception as e:
            n.logger.error(e.args)

    @classmethod
    def status(cls, node = WhiteBoxNode()):
        n = cls(node = node)

        return n.status()


    def _commit(self):

        node_type = self.node.type.value
        node_name = self.node
        node_vol = self.node.volume_oper
        node_svc = self.node.service_port_opr
        node_mgt = docker.from_env()

        node_mgt.containers.run(image = node_type, hostname = node_name, name = node_name, volumes = node_vol,
                                ports = node_svc, detach = True, tty = True, stdin_open = True, privileged = True)

    def _remove(self):
        node_name = self.node.name
        node_env = docker.from_env()
        node_cont = node_env.containers.get(node_name)

        node_cont.stop()
        node_cont.remove()

    def _pause(self):
        node_name = self.node.name
        node_env = docker.from_env()
        node_cont = node_env.containers.get(node_name)
        node_cont.pause()

    def _unpaue(self):
        node_name = self.node.name
        node_env = docker.from_env()
        node_cont = node_env.containers.get(node_name)
        node_cont.unpause()

    def _status(self):
        node_env = docker.from_env()
        node_cont = node_env.containers.get(self.node.name)
        return node_cont.status

    def _exec(self, cmd):
        node_name = self.node.name
        node_env = docker.from_env()
        node_cont = node_env.containers.get(node_name)
        return node_cont.exec_run(cmd = cmd, tty = True, privileged = True)

    def _create_bridge(self):
        if self._exist_bridge(bridge = self.node.bridge_oper):
            raise ValueError("the bridge already has created")

        node_cmd = "ovs-vsctl add-br {bridge} -- set Bridge {bridge} datapath_type=netdev protocols={of_version}"
        node_bridge = self.node.bridge_oper
        node_of_version = self.node.openflow_ver

        self._exec(node_cmd.format(bridge = node_bridge, of_version = node_of_version))

    def _add_port(self, port_name, idx = None):
        if self._exist_port(port = port_name):
            raise ValueError("the port already has included")

        node_cmd = "ovs-vsctl add-port {bridge} {port} -- set Interface {port}"
        if idx is not None:
            node_cmd = node_cmd + " of_port={idx}"

        self._exec(node_cmd)

    def _del_port(self, port_name):
        node_cmd = "ovs-vsctl del-port {bridge} {port}"
        node_bridge = self.node.bridge_oper
        if self._exist_port(port = port_name):
            self._exec(node_cmd.format(bridge = node_bridge, port = port_name))

        else:
            raise ValueError("the port not found")

    def _exist_port(self, port=""):
        cmd = "ovs-vsctl list-ports {bridge}"
        ports = self._exec(cmd = cmd.format(bridge = self.node.bridge_oper))
        p = ports.decode().splitlines()

        if port not in p:
            return False
        return True

    def _exist_bridge(self, bridge=""):
        cmd = "ovs-vsctl list_br"
        bridges = self._exec(cmd = cmd)
        b = bridges.decode().splitlines()

        if bridge not in b:
            return False
        return True

if __name__ == '__main__':

    node = WhiteBoxNode(name = "whx1")

    WhiteBoxCommand.add_node(node = node)
    print(WhiteBoxCommand.status(node = node))