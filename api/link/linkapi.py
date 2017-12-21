import uuid
from enum import Enum

from api.utils import check_not_null


class LinkType(Enum):
    DIRECT = 1
    HOST = 2
    VIRTUAL = 3
    WIFI = 4

    def describe(self):
        return self.name.lower()

    @classmethod
    def is_member(cls, value):
        return any(value == item.value for item in cls)


class Link(object):

    def __init__(self, node_source, node_target, type: LinkType, idx =None, description = None):
        self.__node_source = check_not_null(value = node_source, msg = "the name of source node cannot be null")
        self.__node_target = check_not_null(value = node_target, msg = "the name of target node cannot be null")
        self.__type = check_not_null(value = type, msg = "type of link cannot be null")
        self.__description = description
        self.__port_target = None
        self.__port_source = None
        self.__idx = idx

    @property
    def name(self):
        return "link{idx}".format(idx = self.__idx)

    @name.setter
    def name(self, value):
        pass

    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, value):
        self.__description = value

    @property
    def node_source(self):
        return self.__node_source

    @node_source.setter
    def node_source(self, value):
        pass

    @property
    def node_target(self):
        return self.__node_target

    @node_target.setter
    def node_target(self, value):
        pass

    @property
    def port_source(self):
        return self.__port_source

    @port_source.setter
    def port_source(self, value):
        if self.__port_target is None:
            self.port_source = value
        else:
            pass

    @property
    def port_target(self):
        return self.__port_target

    @port_target.setter
    def port_target(self, value):
        if self.__port_target is None:
            self.__port_target = value
        else:
            pass

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
        if LinkType.is_member(value = value):
            self.__type = value
        else:
            raise ValueError("the type is not member of NodeType")

    @property
    def idx(self):
        return self.__idx

    @idx.setter
    def idx(self, value):
        if self.__idx is None:
            self.__idx = value
        else:
            pass