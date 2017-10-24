import uuid
from node import Node


class Port():
    def __init__(self, label = None, type = None):
        self.id = uuid.uuid4()
        self.label = label
        self.type = type

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, value):
        if value is None:
            if isinstance(value, uuid.uuid4()):
                self.__id = value
            else:
                raise AttributeError("the attribute id must be type UUID 4")

    @property
    def label(self):
        return self.__label

    @label.setter
    def label(self, value):
        if value is not None:
            self.__label = value
        else:
            raise AttributeError("the label port cannot be null")

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
        self.__type = value

    def __str__(self):
        ret = {
            "id": self.id,
            "label": self.label,
            "type": self.type
        }


class VethPort(Port):
    def __init__(self, label = None, type = "Veth"):
        super().__init__(label = label, type = type)

    def create(self, node = Node()):
        ApiPort.create_veth(node = node, port = self)


class ApiPort(object):
    @staticmethod
    def create_veth(node = Node(), port = VethPort()):
        pass
