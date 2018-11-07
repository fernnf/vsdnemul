
from vsdnemul.node import Node, NodeType


class OpenVirtex(Node):

    __image__ = "vsdn/openvirtex"
    __cap_add__ = ["ALL"]
    __volumes__ = {"/sys/fs/cgroup": {"bind": "/sys/fs/cgroup", "mode": "ro"}}
    __type__ = NodeType.HYPERVISOR


    def __init__(self, name, image,):
        super().__init__(name, image, type=self.__type__)
        self.config.update(cap_add=self.__cap_add__)
        self.config.update(volumes=self.__volumes__)

    def getManagerAddr(self):
        return "tcp:{ip}:6633".format(ip=self.getControlIp())

    def createNetwork(self):
        pass

    def createSwitch(self):
        pass

    def createPort(self):
        pass

    def setInterface(self, ifname, encap):
        pass

    def delInterface(self, id):
        pass

    def _Commit(self):
        pass

    def _Destroy(self):
        pass