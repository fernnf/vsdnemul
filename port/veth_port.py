from enum import Enum

from api.log.logapi import get_logger
from api.port.portapi import Port, PortType
from api.utils import rand_interface_name

logger = get_logger("SwitchEthPort")


class VethPortDesc(Enum):
    HOST = 1
    SWITCH = 2

    def describe(self, ):
        return self.name.lower()

    @classmethod
    def has_member(cls, value):
        return any(value == item.value for item in cls)


class HostEthPort(Port):

    def __init__(self, ip, gateway, mtu = "1500"):
        super().__init__(type = PortType.ETHERNET, name = "eth")

        self.__ip = ip
        self.__gate = gateway
        self.__mtu = mtu
        self.__desc = VethPortDesc.HOST
        self.__peer = rand_interface_name()

    @property
    def ip(self):
        return self.__ip

    @ip.setter
    def ip(self, value):
        pass

    @property
    def peer(self):
        return self.__peer

    @peer.setter
    def peer(self, value):
        self.__peer = value

    @property
    def gateway(self):
        return self.__gate

    @gateway.setter
    def gateway(self, value):
        pass

    @property
    def mtu(self):
        return self.__mtu

    @mtu.setter
    def mtu(self, value):
        pass

    @property
    def description(self):
        return self.__desc.describe()

    @description.setter
    def description(self, value):
        pass


class SwitchEthPort(Port):

    def __init__(self, mtu = "1500"):
        super().__init__(name = "eth", type = PortType.ETHERNET)

        self.__mtu = mtu
        self.__peer = rand_interface_name()
        self.__desc = VethPortDesc.SWITCH

    @property
    def mtu(self):
        return self.__mtu

    @mtu.setter
    def mtu(self, value):
        pass

    @property
    def peer(self):
        return self.__peer

    @peer.setter
    def peer(self, value):
        self.__peer = value

    @property
    def description(self):
        return self.__desc.describe()

    @description.setter
    def description(self, value):
        pass