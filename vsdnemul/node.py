import logging
import itertools
from abc import ABC, abstractmethod
from enum import Enum

from vsdnemul.port import PortFabric, Port
from vsdnemul.lib.dockerlib import get_status_node, get_id
'''
Class Abstract to generate new nodes models based on docker file templates. 
'''

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

    def __init__(self, name, image, type: NodeType, **config):
        super(Node, self).__init__()
        self.__name = name
        self.__type = type
        self.__image = image
        self.__id = ""
        self.__cid = ""
        self.__ports = PortFabric(name)
        self.__config = config


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
    def config(self):
        return self.__config

    @config.setter
    def config(self, value):
        pass

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, value):
        self.__id = value

    @property
    def cid(self):
        return get_id(self.name)

    @cid.setter
    def cid(self, value):
        pass

    @property
    def type(self):
        return self.__type.describe()

    @type.setter
    def type(self, value):
        if NodeType.has_member(value=value):
            self.__type = value

    @property
    def status(self):
        try:
            return get_status_node(self.name)
        except:
            return None

    @status.setter
    def status(self, value):
        pass

    @abstractmethod
    def add_port(self):
        pass
    @abstractmethod
    def del_port(self, id):
        pass

    @abstractmethod
    def get_port(self, id):
        pass

    @property
    def get_ports(self):
        return self.__ports.get_ports()

    @get_ports.setter
    def get_ports(self, value):
        pass


    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def destroy(self):
        pass

    def __dict__(self):
        return {
            "id": self.id,
            "cid": self.cid,
            "name": self.name,
            "image": self.image,
            "type": self.type,
            "status": self.status,
            "config": self.config
        }

    def __str__(self):
        return [
            "id={id}".format(id=self.id),
            "cid={cid}".format(cid=self.cid),
            "name={name}".format(name=self.name),
            "image={image}".format(image=self.image),
            "type={type}".format(type=self.type),
            "status={status}".format(status=self.status),
            "config={config}".format(config=self.config)
        ]

class NodeFabric(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.__next_id = itertools.count()
        self.__nodes = {}

    def add_node(self, node: Node):
        key = self.__next_id.__next__()
        node.id = key
        try:
            self.__nodes.update({key: node})
            self.logger.debug("node with id ({id}) has added".format(id=key))
        except Exception as ex:
            self.logger.error(ex.__cause__)
            raise ValueError(ex.__cause__)

    def del_node(self, id):
        if self.id_exist(id):
            del self.__nodes[id]
        else:
            raise ValueError("the id is not found")

    def get_node(self, id):
        return self.__nodes[id]

    def get_nodes(self):
        return self.__nodes

    def id_exist(self, id):
        return any(k == id for k in self.__nodes.keys())

    def start(self):
        try:
            for n in self.__nodes.values():
                n.commit()
                self.logger.info("the new node ({name}) with id ({id}) was added".format(name=n.name, id=n.id))
        except:
            self.logger.error("It cannot create nodes ")

    def stop(self):
        try:
            for n in self.__nodes.values():
                n.destroy()
                self.logger.info("the node ({name}) with id ({id}) was deleted".format(name=n.name, id=n.id))
        except:
            self.logger.error("It cannot delete nodes")
