from enum import Enum
from itertools import count

from api.docker.dockerapi import DockerApi
from api.port.portapi import PortFabric, PortType
from api.utils import check_not_null
from log import Logger

logger = Logger.logger("Node")


class NodeType(Enum):
    HOST = 1
    SWITCH = 2
    ROUTER = 3
    WIFI_ROUTER = 4
    VIRTUAL_SWITCH = 5
    CONTROLLER = 6

    def describe(self):
        return self.name.lower()

    @classmethod
    def has_member(cls, value):
        return any(value == item.value for item in cls)


class Node(object):

    def __init__(self, name, image, type: NodeType, services = None, volume = None, cap_add = None):
        check_not_null(value = name, msg = "the label node cannot be null")
        check_not_null(value = image, msg = "the image name cannot be null")

        self.__name = name
        self.__type = type
        self.__services = services
        self.__image = image
        self.__volume = volume
        self.__cap_add = cap_add
        self.__ports = PortFabric()
        self.__idx = None


    @property
    def idx(self):
        return self.__idx

    @idx.setter
    def idx(self, value):
        if self.__idx is None:
            self.__idx = value
        else:
            pass

    @property
    def image(self):
        return self.__image

    @image.setter
    def image(self, value):
        pass

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        if DockerApi.get_status_node(self.name) == "running":
            DockerApi.rename_node(self.name, new_name = value)
            self.__name = value
        else:
            self.__name = value

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
        if NodeType.has_member(value = value):
            self.__type = value

    @property
    def services(self):
        return self.__services

    @property
    def volume(self):
        return self.__volume

    @volume.setter
    def volume(self, value):
        if self.__volume is None:
            self.__volume = value
        else:
            pass

    @property
    def cap_add(self):
        return self.__cap_add

    @cap_add.setter
    def cap_add(self, value):
        if self.__cap_add is None:
            self.__cap_add = value
        else:
            pass

    @services.setter
    def services(self, value):
        if self.__services is None:
            self.__services = value
        else:
            pass

    @property
    def node_pid(self):
        try:
            return DockerApi.get_pid_node(name = self.name)
        except Exception as ex:
            logger.error(str(ex.args[0]))

    @property
    def node_status(self):
        try:
            return DockerApi.get_status_node(name = self.name)
        except Exception as ex:
            logger.error(str(ex.args[0]))


    @property
    def control_ip(self):
        try:
            return DockerApi.get_control_ip(name = self.name)
        except Exception as ex:
            logger.error(str(ex.args[0]))

    @control_ip.setter
    def control_ip(self, value):
        pass

    def send_cmd(self, cmd = None):
        try:
            return DockerApi.run_cmd(name = self.name, cmd = cmd)
        except Exception as ex:
            logger.error(str(ex.args[0]))

    def get_cli_prompt(self, shell = "bash"):
        try:
            DockerApi.get_shell(name = self.name, shell = shell)
        except Exception as ex:
            logger.error(str(ex.args[0]))

    def add_node_port(self, type: PortType):
        try:
            return self.__ports.add_port(type = type)
        except Exception as ex:
            logger.error(str(ex.args[0]))

    def del_node_port(self, name):
        try:
            self.__ports.del_port(name = name)
        except Exception as ex:
            logger.error(str(ex.args[0]))

    def is_port_exist(self, name):
        return self.__ports.is_exist(name = name)

    def get_ports(self):
        return self.__ports.get_ports()


class NodeFabric(object):
    def __init__(self):
        self.__nodes = {}
        self.__node_idx = count()

    def add_node(self, node):
        if not self.__exist_node(name = node.name):
            key = self.__node_idx.__next__()
            node.idx = key
            self.__nodes.update({key: node})
            return node
        else:
            raise ValueError("the node object already exists")

    def del_node(self, name):
        if self.__exist_node(name = name):
            key = self.__get_index(name = name)
            del self.__nodes[key]
        else:
            ValueError("the node was not found")

    def update_node(self, idx, node):
        if self.__exist_node(idx = idx):
            self.__nodes.update({idx: node})
        else:
            ValueError("the node was not found")

    def get_node(self, name):

        if self.__exist_node(name = name):
            key = self.get_index(name = name)
            return self.__nodes[key]
        else:
            ValueError("the node was not found")

    def get_nodes(self):
        return self.__nodes.copy()

    def is_exist(self, name):
        return self.__exist_node(name = name)

    def get_index(self, name):
        if self.__exist_node(name = name):
            return self.__get_index(name = name)
        else:
            ValueError("the node was not found")

    def __get_index(self, name):
        for k, n in self.__nodes.items():
            if n.name.__eq__(name):
                return k

    def __exist_node(self, name = None, idx = None):

        if name is not None:
            key = self.__get_index(name = name)
            if key is not None:
                return True

        if idx is not None:
            if idx in self.__nodes.keys():
                return True

        return False
