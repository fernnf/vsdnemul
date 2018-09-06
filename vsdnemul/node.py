import itertools
import logging
from abc import ABC, abstractmethod
from enum import Enum
from uuid import uuid4 as rand_id

from vsdnemul.lib.dockerlib import get_status_node, get_id

'''
Class Abstract to generate new nodes models based on docker file templates. 
'''

logger = logging.getLogger(__name__)

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

    __ports__ = ""
    __volumes__ = ""
    __cap_add__ = ""
    __image__ = ""
    __type__ = ""

    def __init__(self, name, image, type: NodeType):
        super(Node, self).__init__()
        self.__name = name
        self.__type = type
        self.__image = image
        self.__cid = None
        self.config = dict()
        self.interfaces = dict()
        self.count_interface = itertools.count(start=1, step=1)


    def getName(self):
        return self.__name

    def getImage(self):
        return self.__image

    def getStatus(self):
        try:
            return get_status_node(self.__name)
        except:
            return None

    def getId(self):
        try:
            return get_id(self.__name)
        except:
            return None

    def getType(self):
        return self.__type

    def setType(self, type: NodeType):
        self.__type = type

    @abstractmethod
    def setInterface(self, ifname, encap):
        pass

    @abstractmethod
    def delInterface(self, id):
        pass

    @abstractmethod
    def _Commit(self):
        pass

    @abstractmethod
    def _Destroy(self):
        pass

    def __dict__(self):
        return {
            "id": self.getId(),
            "name": self.getName(),
            "image": self.getImage(),
            "type": self.getType().name,
            "status": self.getStatus(),
        }

    def __str__(self):
        return [
            "id={id}".format(id=self.getId()),
            "name={name}".format(name=self.getName()),
            "image={image}".format(image=self.getImage()),
            "type={type}".format(type=self.getType().name),
            "status={status}".format(status=self.getStatus())
        ]


class NodeFabric(object):

    def __init__(self):
        self.__nodes = {}

    def isExist(self, name):
        return any(k == name for k in self.__nodes.keys())

    def addNode(self, node):
        key = node.getName()
        if not self.isExist(name=key):
            self.__nodes.update({key: node})
            node._Commit()
            return node
        else:
            raise ValueError("the node not found")

    def delNode(self, name):
        if self.isExist(name):
            node = self.__nodes[name]
            node._Destroy()
            del self.__nodes[name]
        else:
            raise ValueError("the node not found")

    def getNode(self, name):
        return self.__nodes[name]

    def getNodes(self):
        return self.__nodes
