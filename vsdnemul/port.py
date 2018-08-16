import itertools
from enum import Enum
from uuid import uuid4 as rand_id


class PortType(Enum):
    ETHERNET = "vif"
    OPTICAL = "vopt"
    RADIO = "vwifi"
    HOST = "host"

    def describe(self):
        return self.name.lower()

    @classmethod
    def is_member(cls, value):
        return any(value.value == item.value for item in cls)


class Port(object):

    def __init__(self, value, type: PortType):
        self.__type = type
        self.__value = value
        self.__id = rand_id()

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, value):
        pass

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, v):
        if self.__value is None:
            self.__value = v
        else:
            pass

    @property
    def name(self):
        return "{type}{value}".format(type=self.__type.value, value=self.value)

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
            "id": "{id}".format(self.id),
            "object": "{object}".format(self.__name__),
            "type": "{type}".format(self.type),
            "name": "{name}".format(self.name),
            "node": "{node_name}".format(self.node_name),
        }


class PortFabric(object):

    def __init__(self, node_name):
        self.__ports = {}
        self.__count = itertools.count()
        self.__node = node_name

    def add_port(self, type: PortType):
        port = Port(value=self.__count.__next__(), type=type, node_name=self.__node)
        self.__ports.update({port.id: port})
        return port

    def del_port(self, id):
        if not self.is_exist(id):
            raise ValueError("the port not found")

        del self.__ports[id]

    def update_port(self, id, port):
        if not id.__eq__(port.id):
            raise ValueError("the port id is not equal object")

        if not self.is_exist(id):
            raise ValueError("the port not found")

        self.__ports.update({port.id: port})

    def get_ports(self):
        return self.__ports.values()

    def get_ids(self):
        return self.__ports.keys()

    def get_port(self, id):
        if not self.is_exist(id):
            raise ValueError("the port not found")

        return self.__ports[id]

    def from_node(self, id):
        if not self.is_exist(id):
            raise ValueError("the port not found")

        return self.__ports[id].node_name

    def is_exist(self, id):
        return id in self.__ports
