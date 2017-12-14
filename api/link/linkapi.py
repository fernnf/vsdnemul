import uuid

from api.node.nodeapi import Node
from api.utils import check_not_null


class Link(object):

    def __init__(self, type, node_source, node_target, mtu = "1500"):
        self.__node_source = check_not_null(value = node_source, msg = "the name of source node cannot be null")
        self.__node_target = check_not_null(value = node_target, msg = "the name of target node cannot be null")
        self.__type = check_not_null(value = type, msg = "type of link cannot be null")
        self.__id = str(uuid.uuid4())[0:8]
        self.__mtu = mtu


    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, value):
        pass

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
        return self.__node_source + "-" + self.__node_target

    @port_source.setter
    def port_source(self, value):
        pass

    @property
    def port_target(self):
        return self.__node_target+ "-" + self.__node_source

    @port_target.setter
    def port_target(self, value):
        pass

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
        pass

    @property
    def mtu(self):
        return self.__mtu

    @mtu.setter
    def mtu(self, value):
        pass