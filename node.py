import logging
from enum import Enum

from functions import ApiNode, ApiService


class TypeNode(Enum):
    Host = "vsdn/host"
    WhiteBox = "vsdn/whitebox"


# noinspection PyAttributeOutsideInit
class Node(object):
    logger = logging.getLogger("node.Node")

    def __init__(self, name = None, type = None, service = None):
        self.name = name
        self.type = type
        self.service = service
        self.links = {}

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        if value is None:
            raise AttributeError("the name node cannot be null")
        elif not isinstance(value, str):
            raise AttributeError("the name must be string")
        self.__name = value

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
        if value is None:
            raise AttributeError("the type node cannot be null")
        elif not isinstance(value, str):
            raise AttributeError("the type must be string")
        self.__type = value

    def __str__(self):
        str = {
            "name": self.name,
            "type": self.type,
            "service": self.service,
            "links": self.links
        }

        return str.__str__()


class WhiteBox(Node):
    def __init__(self, name = None):
        super().__init__(name = name, type = TypeNode.WhiteBox.value,
                         service = {'22/tcp': None, '6633/tcp': None, '6640/tcp': None, '6653/tcp': None})

    @classmethod
    def getNode(cls, subject):
        node = {
            "name": None,
            "type": None
        }
        node.update(subject)

        if node["type"] is "WhiteBox":
            n = cls(name = node["name"])
            return n
        else:
            raise ValueError("the type value is unknown")


class Host(Node):
    def __init__(self, name = None, ip = None, mask = None):
        super().__init__(name = name, type = TypeNode.Host.value, service = {'22/tcp': None})

        self.ip = ip
        self.mask = mask

    @property
    def ip(self):
        return self.__ip

    @ip.setter
    def ip(self, value):
        try:
            self.__ip = value
        except ValueError as ex:
            raise ValueError("the address is invalid")

    @property
    def mask(self):
        return self.__mask

    @mask.setter
    def mask(self, value):
        try:
            self.__mask = value
        except ValueError as ex:
            raise ValueError("the mask address is invalid")

    @classmethod
    def getNode(cls, subject):
        node = {
            "name": None,
            "type": None,
            "ip": None,
            "mask": None
        }
        node.update(subject)

        if node["type"] is "Host":
            n = cls(name = node["name"], ip = node["ip"], mask = node["mask"])
            return n
        else:
            raise ValueError("the type value is unknown")


class NodeCommand(object):
    @staticmethod
    def setController(node, ip, port):
        try:
            ApiService.serviceSetNodeController(node.name, ip = ip, port = port)
        except Exception as ex:
            print("Error: " + ex.args.__str__())

    @staticmethod
    def create(node):
        try:
            ApiNode.nodeCreate(name = node.name, type = node.type, service = node.service)
        except Exception as ex:
            print("Error: " + ex.args.__str__())

    @staticmethod
    def delete(node):
        try:
            ApiNode.nodeDelete(name = node.name)
        except Exception as ex:
            print("Error: " + ex.args.__str__())

    @staticmethod
    def sendCmd(node, cmd):
        try:
            ApiNode.nodeSendCmd(name = node.name, cmd = cmd)
        except Exception as ex:
            print("Error: " + ex.args.__str__())
