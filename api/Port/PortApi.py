from api.utils import check_not_null


class Port(object):

    def __init__(self, ifname, type, netns=None, ip=None, gateway = None):
        self.__ifname = ifname
        self.__type = type
        self.__ip = ip
        self.__gateway = gateway
        self.__netns = netns

    @property
    def ifname(self):
        return self.__ifname

    @property
    def type(self):
        return self.__type

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
    def netns(self):
        return self.__netns

    @netns.setter
    def netns(self, value):
        self.__netns = value


class PortFabric(object):
    def __init__(self):
        self.__fabric = []

    def add_port(self, port: Port):
        check_not_null(port, "the port object cannot be null")
        if not self.__fabric.__contains__(port):
            return self.__fabric.append(port)
        else:
            raise ValueError("the port object already exist")

    def del_port(self, port: Port):
        check_not_null(port, "the port object cannot be null")
        if self.__fabric.__contains__(port):
            self.__fabric.remove(port)
        else:
            raise ValueError("the port object not exist")

    def get_index(self, port: Port):
        check_not_null(port, "the port object cannot be null")
        if self.__fabric.__contains__(port):
            return self.__fabric.index(port)
        else:
            raise ValueError("the port object not exist")