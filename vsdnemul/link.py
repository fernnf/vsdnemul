from abc import ABC, abstractmethod
from enum import Enum
from uuid import uuid4 as rand_id

from vsdnemul.node import Node


class LinkType(Enum):
    DIRECT = "direct"
    HOST = "host"
    VIRTUAL = "virtual"
    WIFI = "wifi"

    def describe(self):
        return self.name.lower()

    def typeName(self):
        return self.value

    @classmethod
    def is_member(cls, value):
        return any(value == item.value for item in cls)


class LinkEncap(Enum):
    ETHERNET = "vif"
    OPTICAL = "vopt"
    RADIO = "vwifi"
    HOST = "vht"

    def describe(self):
        return self.name.lower()

    def portName(self):
        return self.value

    @classmethod
    def is_member(cls, value):
        return any(value.value == item.value for item in cls)


class Link(ABC):

    def __init__(self, node_source: Node, node_target: Node, type: LinkType, encap: LinkEncap):
        super(Link, self).__init__()
        self.__source = node_source
        self.__target = node_target
        self.__type = type
        self.__encap = encap
        self.__id = rand_id()
        self.__port_source = None
        self.__port_target = None

    def getName(self):
        return "link{id}".format(id=self.__id[:8])

    def getType(self):
        return self.__type

    def getEncap(self):
        return self.__encap

    def getId(self):
        return self.__id

    def getSource(self):
        return self.__source.getName()

    def getTarget(self):
        return self.__target.getName()

    def getPortSource(self):
        return self.__port_source

    def setPortSource(self, source: int):
        self.__port_source = source

    def getPortTarget(self):
        return self.__port_target

    def setPortTarget(self, target: int):
        self.__port_target = target

    @abstractmethod
    def _commit(self):
        pass

    @abstractmethod
    def _destroy(self):
        pass

    def __dict__(self):
        return {
            "id": "{id}".format(id=self.getId()),
            "name": "{name}".format(name=self.getName()),
            "type": "{type}".format(type=self.getType()),
            "encap": "{encap}".format(encap=self.getEncap()),
            "node_source": "{node_src}".format(node_src=self.getSource()),
            "node_target": "{node_tgt}".format(node_tgt=self.getTarget()),
            "port_source": "{port_src}".format(port_src=self.getPortSource()),
            "port_target": "{port_tgt}".format(port_tgt=self.getTarget()),
        }


class LinkFabric(object):
    def __init__(self):
        self.__links = {}

    def isExist(self, id):
        return id in self.__links

    #FIXME: To create search method more opitmized
    def isExistLink(self, source: Node, target: Node):
        for l in self.__links.values():
            s = l.getSource()
            t = l.getTarget()
            if s.__eq__(source.getName() or target.getName()):
                if t.__eq__(source.getName() or target.getName()):
                    return True

        return False


    def addLink(self, link):
        key = link.getId()

        if self.isExist(key):
            raise ValueError("the link object already exists")

        elif self.isExistLink(link.getSource(), link.getTarget()):
            raise ValueError("the link object already exists")
        else:
            self.__links.update({key: link})

    def delLink(self, id):
        if self.isExist(id):
            del self.__links[id]
        else:
            ValueError("the node not found")

    def getLinks(self):
        return self.__links

    def getLink(self, id):
        if self.isExist(id):
            return self.__links[id]
        else:
            ValueError("the link was not found")

    def updateLink(self, id, link):
        key = link.getId()

        if not id.__eq__(key):
            raise ValueError("Link id and object are different")

        if self.isExist(id):
            self.__links.update({key: link})
        else:
            ValueError("the node was not found")
