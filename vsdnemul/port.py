import itertools
from enum import Enum
from uuid import uuid4 as rand_id


class PortType(Enum):
    ETHERNET = "vif"
    OPTICAL = "vopt"
    RADIO = "vwifi"
    HOST = "vht"

    def describe(self):
        return self.name.lower()

    @classmethod
    def is_member(cls, value):
        return any(value.value == item.value for item in cls)


class Port(object):

    def __init__(self, type: PortType):
        self.__type = type
        self.__id = ""

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, value):
        self.__id = value

    @property
    def name(self):
        return "{type}{id}".format(type=self.__type.value, id=self.id)

    @name.setter
    def name(self, value):
        pass

    @property
    def type(self):
        return self.__type.describe()

    @type.setter
    def type(self, t):
        if PortType.is_member(value=t):
            self.__type = t
        else:
            raise ValueError("the value is not member of PortType")

    def __dict__(self):
        return {
            "id": "{id}".format(id=self.id),
            "type": "{type}".format(type=self.type),
            "name": "{name}".format(name=self.name),
        }

    def __str__(self):
        return [
            "id={id}".format(id=self.id),
            "type={type}".format(type=self.type),
            "name={name}".format(name=self.name)
        ]


class PortFabric(object):

    def __init__(self, node_name):
        self.__node = node_name
        self.__next_id = itertools.count()
        self.__ports = {}


    def add_port(self, port: Port):
        key = self.__next_id.__next__()
        port.id = key
        self.__ports.update({key: port})
        return key

    def del_port(self, id):
        if self.is_exist(id=id):
            del self.__ports[id]
        else:
            raise ValueError("the key is not found")

    def get_ports(self):
        return self.__ports.copy()

    def get_ids(self):
        return self.__ports.keys()

    def get_port(self, id):
        if self.is_exist(id):
            return self.__ports[id]
        else:
            raise ValueError("the key is not exist")

    def is_exist(self, id):
        return id in self.__ports.keys()
