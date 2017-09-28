import logging
from enum import Enum
from functions import ApiNode


class TypeNode(Enum):
    Host = "ubuntu:latest"
    WhiteBox = "vsdn/whitebox"


# noinspection PyAttributeOutsideInit
class Node(object):
    logger = logging.getLogger("node.Node")

    def __init__(self, name = None, type = None, service = {}):
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

        return str


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


class NodeCommand(object):

    def __init__(self, node):
        self.__node = node
        self.__logger = logging.getLogger("node.NodeCommand")

    @staticmethod
    def create(node):
        try:
            ApiNode.create_node(node.name, node.type, node.service)
        except Exception as ex:
            print(ex.args)

    @staticmethod
    def delete(node):
        try:
            ApiNode.delete_node(node.name)
        except Exception as ex:
            print(ex.args)


if __name__ == '__main__':


    try:
        node = WhiteBox(name = "1")
        print(node.__str__())
    except Exception as ex:
        print(ex.args[0])


