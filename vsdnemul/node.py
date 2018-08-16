import logging
from abc import ABC, abstractmethod
from enum import Enum

from vsdnemul.port import PortFabric, Port


class NodeType(Enum):
    HOST = "HOST"
    SWITCH = "SWITCH"
    ROUTER = "ROUTER"
    WIFI_ROUTER = "WIFI_ROUTER"
    CONTROLLER = "CONTROLLER"
    SERVER = "SERVER"
    HYPERVISOR = "SDN HYPERVISOR"

    def describe(self):
        return self.name.lower()

    @classmethod
    def has_member(cls, value):
        return any(value == item.value for item in cls)


class Node(ABC):

    def __init__(self, name, image, type: NodeType, **params):
        super(Node, self).__init__()
        self.__name = name
        self.__type = type
        self.__image = image
        self.__ports = PortFabric(node_name=name)

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
        pass

    @property
    def type(self):
        return self.__type.describe()

    @type.setter
    def type(self, value):
        if NodeType.has_member(value=value):
            self.__type = value

    @abstractmethod
    def set_port(self, port: Port):
        pass

    @abstractmethod
    def del_port(self, id):
        pass

    @abstractmethod
    def get_ports(self):
        pass

    @abstractmethod
    def get_cli(self, type="bash"):
        pass

    @abstractmethod
    def get_id(self):
        pass

    @abstractmethod
    def get_status(self):
        pass

    @abstractmethod
    def get_control_ip(self):
        pass

    @abstractmethod
    def get_pid(self):
        pass

    @abstractmethod
    def change_name(self, new_name):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def destroy(self):
        pass


class NodeFabric(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.__nodes = {}

    def add_node(self, node: Node):
        try:
            node.commit()
            key = node.get_id()
            self.__nodes.update({key: node})
        except Exception as ex:
            self.logger.error(ex.__cause__)
            raise RuntimeError(ex.__cause__)

    def del_node(self, node_id):
        if self.id_exist(node_id):
            node = self.get_node(node_id)
            node.destroy()
            del self.__nodes[node_id]
        else:
            raise RuntimeError("the node is not found")

    def get_node(self, node_id):

        if self.id_exist(node_id):
            return self.__nodes[node_id]
        else:
            raise RuntimeError("the node is not found")

    def get_nodes(self):
        return self.__nodes.copy()

    def id_exist(self, node_id):
        return node_id in self.__nodes.keys()

    def node_exist(self, name):
        for v in self.__nodes.values():
            if v.name.__eq__(name):
                return True
        return False

    def get_id(self, name):
        for k, v in self.__nodes.items():
            if v.name.__eq__(name):
                return k
        return None
