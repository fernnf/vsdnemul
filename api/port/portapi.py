import itertools
from enum import Enum

from api.utils import check_not_null


class PortType(Enum):
    ETHERNET = 1
    OPTICAL = 2
    RADIO = 3

    def describe(self):
        return self.name.lower()

    @classmethod
    def is_member(cls, value):
        return any(value.value == item.value for item in cls)


class Port(object):

    def __init__(self, name, type: PortType):
        self.__name = check_not_null(name, "the name port cannot be null")
        self.__type = check_not_null(type, "the type port cannot be null")
        self.__idx = None

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
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

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

    def add_port(self, port):
        check_not_null(port, "the port object cannot be null")

        if not self.__exist_port(name = port.name):
            key = self.__count.__next__()
            port.idx = key
            port.name = port.name+key
            self.__ports.update({key: port})
            return key
        else:
            raise ValueError("The port already exists")

    def del_port(self, name = None, idx = None):
        if self.__exist_port(name = name, idx = idx):
            if name is not None:
                key = self.get_index(name = name)
                del self.__ports[key]
            else:
                del self.__ports[idx]
        else:
            raise ValueError("the port was not found")

    def update_port(self, idx, port):
        if self.__exist_port(idx = idx):
            self.__ports.update({idx: port})
        else:
            raise ValueError("The port was not found")

    def get_ports(self):
        return self.__ports.copy()

    def is_exist(self, name):
        return self.__exist_port(name = name)

    def get_index(self, name):
        check_not_null(name, "the name port object cannot be null")
        if self.__exist_port(name = name):
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
