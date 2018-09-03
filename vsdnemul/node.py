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

    def __init__(self, name, image, type: NodeType):
        super(Node, self).__init__()
        self.__name = name
        self.__type = type
        self.__image = image
        self.__id = rand_id()
        self.__cid = None
        self._config = dict()

    def getName(self):
        return self.__name

    def getImage(self):
        return self.__image

    def getId(self):
        return self.__id

    def getStatus(self):
        try:
            return get_status_node(self.__name)
        except:
            return None

    def getCid(self):
        try:
            return get_id(self.__name)
        except:
            return None

    def getType(self):
        return self.__type

    def setType(self, type: NodeType):
        self.__type = type

    @abstractmethod
    def _commit(self):
        pass

    @abstractmethod
    def _destroy(self):
        pass

    def __dict__(self):
        return {
            "id": self.getId(),
            "cid": self.getCid(),
            "name": self.getName(),
            "image": self.getImage(),
            "type": self.getType().name,
            "status": self.getStatus(),
        }

    def __str__(self):
        return [
            "id={id}".format(id=self.getId()),
            "cid={cid}".format(cid=self.getCid()),
            "name={name}".format(name=self.getName()),
            "image={image}".format(image=self.getImage()),
            "type={type}".format(type=self.getType().name),
            "status={status}".format(status=self.getStatus())
        ]


class NodeFabric(object):

    def __init__(self):
        self.__nodes = {}

    def isExist(self, id):
        return any(k == id for k in self.__nodes.keys())

    def addNode(self, node: Node):
        key = node.getId()
        if not self.isExist(id=key):
            self.__nodes.update({key: node})
        else:
            raise ValueError("the node not found")

    def delNode(self, id):
        if self.isExist(id):
            del self.__nodes[id]
        else:
            raise ValueError("the node not found")

    def getNode(self, id):
        return self.__nodes[id]

    def getNodes(self):
        return self.__nodes

    def start(self):
        try:
            for n in self.__nodes.values():
                n._commit()
                logger.info("the new node ({name}) with id ({id}) was added".format(name=n.name, id=n.id))
        except:
            logger.error("It cannot create nodes ")

    def stop(self):
        try:
            for n in self.__nodes.values():
                n._destroy()
                logger.info("the node ({name}) with id ({id}) was deleted".format(name=n.name, id=n.id))
        except:
            logger.error("It cannot delete nodes")
