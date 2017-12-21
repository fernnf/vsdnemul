from selinux import selabel_close

from api.utils import check_not_null
import itertools
from enum import Enum


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

    def __init__(self, idx, type, mtu = "1500", ip=None, gateway = None):
        self.__name = "eth{idx}".format(idx)
        self.__type = type
        self.__ip = ip
        self.__gateway = gateway
        self.__mtu = mtu


    @property
    def name(self):
        return self.__name

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

    @property
    def ip(self):
        return self.__ip

    @ip.setter
    def ip(self, value):
        self.__ip = value

    @property
    def gateway(self):
        return self.__gateway

    @gateway.setter
    def gateway(self, value):
        self.__gateway = value

    @property
    def mtu(self):
        return self.__mtu

    @mtu.setter
    def mtu(self, value):
        pass


class PortFabric(object):

    def __init__(self):
        self.__ports = {}
        self.__count = itertools.count()

    def add_port(self, port):
        check_not_null(port, "the port object cannot be null")

        if self.__get_index(name = port.name) is None:
            key = self.__count.__next__()
            self.__ports.update({key: port})
        else:
            raise ValueError("The port already exists")

    def del_port(self, name = None, idx = None):

        if name is not None:
            key = self.__get_index(name = name)
            if key is None:
                return False
            else:
                del self.__ports[key]
                return True

        if idx is not None:
            if idx in self.__ports:
                del self.__ports[idx]
                return True

        return False

    def get_ports(self):
        return self.__ports.copy()

    def get_index(self, name):
        check_not_null(name, "the name port object cannot be null")

        key = self.__get_index(name = name)

        if key is not None:
            return key

    def __get_index(self, name):
        for k,v in self.__ports.items():
            if v.name.__eq__(name):
                return k

        return None