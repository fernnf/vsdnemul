import itertools
from enum import Enum
from abc import ABCMeta

from api.utils.utils import check_not_null


class PortType(Enum):
    ETHERNET = "data"
    OPTICAL = "opt"
    RADIO = "wifi"

    def describe(self):
        return self.name.lower()

    @classmethod
    def is_member(cls, value):
        return any(value.value == item.value for item in cls)


class Port(object):

    def __init__(self, type: PortType, idx = None):
        self.__type = check_not_null(type, "the type port cannot be null")
        self.__idx = idx

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
    def name(self):
        return "{type}{idx}".format(type = self.type.value, idx = self.idx)

    @name.setter
    def name(self, value):
        pass

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
        if PortType.is_member(value = value):
            self.__type = value
        else:
            raise ValueError("the value is not member of PortType")


class PortFabric(object):

    def __init__(self):
        self.__ports = {}
        self.__count = itertools.count()

    def add_port(self, type: PortType):
        port = Port(type = type)
        key = self.__count.__next__()
        port.idx = key
        self.__ports.update({key: port})
        return port

    def del_port(self, name):
        check_not_null(name, "the port name cannot be null")
        if self.is_exist(name = name):
            key = self.get_index(name = name)
            del self.__ports[key]
        else:
            raise ValueError("the port was not found")

    def update_port(self, idx, port):
        if self.is_exist(name = port.name):
            self.__ports.update({idx: port})
        else:
            raise ValueError("The port was not found")

    def get_ports(self):
        return self.__ports.copy()

    def get_port(self, name):
        if self.__exist_port(name = name):
            key = self.get_index(name = name)
            return self.__ports[key]

    def is_exist(self, name):
        return self.__exist_port(name = name)

    def get_index(self, name):
        check_not_null(name, "the name port object cannot be null")
        if self.is_exist(name = name):
            return self.__get_index(name = name)
        else:
            raise ValueError("the port was not found")

    def __get_index(self, name):
        for k, v in self.__ports.items():
            if v.name.__eq__(name):
                return k

    def __exist_port(self, name = None, idx = None):
        if name is not None:
            key = self.get_index(name = name)
            if key is not None:
                return True

        if idx is not None:
            if idx in self.__ports.keys():
                return True

        return False
