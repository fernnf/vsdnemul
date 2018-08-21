import random
from vsdnemul.port import Port, PortType

def rand_mac():
    return ("%02x:%02x:%02x:%02x:%02x:%02x" %
            (random.randint(0, 255),
             random.randint(0, 255),
             random.randint(0, 255),
             random.randint(0, 255),
             random.randint(0, 255),
             random.randint(0, 255)))


class Ethernet(Port):
    def __init__(self, mac=None, ip=None, mask=None):
        super(Ethernet, self).__init__(type=PortType.ETHERNET)
        self.__mac = (rand_mac() if mac is None else mac)
        self.__ip = ip
        self.__mask = mask

    @property
    def mac(self):
        return self.__mac

    @mac.setter
    def mac(self, value):
        pass

    @property
    def ip(self):
        return self.__ip

    @ip.setter
    def ip(self, value):
        pass

    @property
    def mask(self):
        return self.__mask

    @mask.setter
    def mask(self, value):
        pass

    def __str__(self):
        result = super().__str__()
        result.append("mac={mac}".format(mac=self.mac))
        return result

    def __dict__(self):
        result = super().__dict__()
        result.update({"mac": self.mac})
        return result