from enum import Enum, unique

@unique
class PortType(Enum):
    Ethernet = "ethernet"
    
    def __str__(self):
        return PortType.Ethernet.name


class Port(object):

    def __init__(self, name="", status="", type = PortType()):
        self.name = name
        self.status = status
        self.type = type

    @property
    def name(self):
        return self.__name
    
    @name.setter
    def name(self, name):
        if name is not None:
            self.__name = name
        else:
            raise ValueError("name cannot be null")
        
    @property
    def status(self):
        return self.__status
    
    @status.setter
    def status(self, status):
        self.__status = status
    
    @property
    def type(self):
        return self.__type
    
    @type.setter
    def type(self, type = PortType()):
        if type is not None:
            self.__type = type.name
        else:
            raise ValueError("type cannot be null")
    

