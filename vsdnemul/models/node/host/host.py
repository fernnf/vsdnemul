import logging

from vsdnemul.lib import dockerlib as docker
from vsdnemul.lib import iproutelib as iproute
from vsdnemul.lib import utils
from vsdnemul.node import Node, NodeType

logger = logging.getLogger(__name__)


def _GetManagerAddr(node):
    def get_ip():
        return iproute.get_interface_addr(ifname="eth0", netns=node)

    return "tcp:{ip}:6640".format(ip=get_ip())


class Host(Node):

    __volumes__ = {"/sys/fs/cgroup": {"bind": "/sys/fs/cgroup", "mode": "ro"}}
    __cap_add__ = ["ALL"]
    __image__ = "vsdn/host"
    __type__ = NodeType.HOST

    def __init__(self, name, ip =None, mask = None, gateway = None):

        super(Host, self).__init__(name, image=self.__image__, type=self.__type__)
        self.config.update(volumes=self.__volumes__)
        self.config.update(cap_add=self.__cap_add__)

        self.__ip = ip
        self.__mask = mask
        self.__gateway = gateway

    def getControlAddr(self):
        try:
            return _GetManagerAddr(self.getName())
        except Exception as ex:
            logger.error(ex.args[0])
            return None

    def getIp(self):
        return self.__ip

    def setIp(self, value):
        self.__ip = value

    def getMask(self):
        return self.__mask

    def setMask(self, value):
        self.__mask =  value

    def getGateway(self):
        return self.__gateway

    def setGateway(self, value):
        self.__gateway = value

    def sendCommand(self, value):
        try:
            return docker.run_cmd(name = self.getName(), cmd = value)
        except Exception as ex:
            logger.error(str(ex.args[0]))

    def setInterface(self, ifname, encap):
        id = str(self.count_interface.__next__())
        interface = encap.portName() + id
        addr = ""
        if self.__ip is not None:
            if self.__mask is not None:
                addr ="{ip}/{mask}".format(ip=self.__ip, mask=self.__mask)
            else:
                raise ValueError("for setting the ip is need a mask address")

        try:
            iproute.add_port_ns(ifname=ifname, netns=self.getName(), new_name=interface)
            iproute.config_port_address(ifname=interface, ip_addr=addr, gateway=self.getGateway(), netns=self.getName())
            utils.disable_rx_off(netns=self.getName(), port_name=interface)
            self.interfaces.update({id: interface})
            return id
        except Exception as ex:
            logger.error(ex.args[0])


    def delInterface(self, id):
        interface = self.interfaces[id]
        try:
            iproute.delete_port(ifname=interface, netns=self.getName())
            del (self.interfaces[id])
        except Exception as ex:
            logger.error(ex.args[0])

    def _Commit(self):
        try:
            docker.create_node(name=self.getName(), image=self.getImage(), **self.config)
            logger.info("the new host ({name}) node was created".format(name=self.getName()))
        except Exception as ex:
            logger.error(ex.args[0])

    def _Destroy(self):
        try:
            docker.delete_node(name=self.getName())
            logger.info("the host ({name}) node was deleted".format(name=self.getName()))
        except Exception as ex:
            logger.error(ex.args[0])
