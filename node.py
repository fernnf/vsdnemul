import logging
import docker
import pyroute2

from enum import Enum
from port import Port

from functions import ApiNode, ApiService



_client_docker = docker.from_env()
_client_iproute = pyroute2.IPRoute()

class TypeNode(Enum):
    Host = "vsdn/host"
    WhiteBox = "vsdn/whitebox"


# noinspection PyAttributeOutsideInit
class Node(object):
    logger = logging.getLogger("node.Node")

    def __init__(self, label = None, type = None, service = None, image = None):
        self.label = label
        self.type = type
        self.service = service
        self.image = image
        self._ports = []

    @property
    def image(self):
        return self.__image

    @image.setter
    def image(self, value):
        if value is not None:
            self.__image = value
        else:
            raise AttributeError("the image name cannot be null")

    @property
    def label(self):
        return self.__name

    @label.setter
    def label(self, value):
        if value is not None:
            self.__name = value
        else:
            raise AttributeError("the label node cannot be null")

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
        if value is not None:
            self.__type = value
        else:
            raise AttributeError("the type node cannot be null")

    def __str__(self):
        str = {
            "label": self.label,
            "type": self.type,
            "service": self.service,
            "ports": self._ports
        }

        return str.__str__()


class WhiteBox(Node):
    def __init__(self, label = None):
        super().__init__(label = label,
                         type = "WhiteBox",
                         service = {'22/tcp': None, '6633/tcp': None, '6640/tcp': None, '6653/tcp': None},
                         image = "vsdn/whitebox")

    @property
    def control_ip(self):
        return ApiNode.has_node_ip_management(label = self.label)

    @property
    def service_exposed_port(self, service_port = None):
        return ApiNode.has_node_service_exposed_port(label = self.label, service_port = service_port)

    @property
    def node_pid(self):
        return ApiNode.has_node_pid(label = self.label)

    def send_cmd(self, cmd = None):
        return ApiNode.node_send_cmd(self.label, cmd = cmd)

    def has_port(self, label = None):
        for p in self._ports:
            if p.label == label:
                return True
        return False

    def add_port(self, port = Port()):
        self._ports.append(port)

    def get_ports(self):
        return self._ports

    def create(self):
        pass

    def delete(self):
        pass

    def __ovs_add_port_to_bridge(self, port):
        c


class Host(Node):
    def __init__(self, label = None, ip = None, mask = None):
        super().__init__(label = label, type = TypeNode.Host.value, service = {'22/tcp': None})

        self.ip = ip
        self.mask = mask

    @property
    def ip(self):
        return self.__ip

    @ip.setter
    def ip(self, value):
        try:
            self.__ip = value
        except ValueError as ex:
            raise ValueError("the address is invalid")

    @property
    def mask(self):
        return self.__mask

    @mask.setter
    def mask(self, value):
        try:
            self.__mask = value
        except ValueError as ex:
            raise ValueError("the mask address is invalid")

    @classmethod
    def getNode(cls, subject):
        node = {
            "label": None,
            "type": None,
            "ip": None,
            "mask": None
        }
        node.update(subject)

        if node["type"] is "Host":
            n = cls(name = node["label"], ip = node["ip"], mask = node["mask"])
            return n
        else:
            raise ValueError("the type value is unknown")


class NodeCommand(object):
    @staticmethod
    def setController(node, ip, port):
        try:
            ApiService.serviceSetNodeController(node.label, ip = ip, port = port)
        except Exception as ex:
            print("Error: " + ex.args.__str__())

    @staticmethod
    def create(node):
        try:
            ApiNode.nodeCreate(name = node.label, type = node.type, service = node.service)
        except Exception as ex:
            print("Error: " + ex.args.__str__())

    @staticmethod
    def delete(node):
        try:
            ApiNode.nodeDelete(name = node.label)
        except Exception as ex:
            print("Error: " + ex.args.__str__())

    @staticmethod
    def sendCmd(node, cmd):
        try:
            ApiNode.nodeSendCmd(name = node.label, cmd = cmd)
        except Exception as ex:
            print("Error: " + ex.args.__str__())


class ApiNode(object):

    @staticmethod
    def create_node(label, type, service):
        _client_docker.containers \
            .run(image = type,
                 hostname = label,
                 name = label,
                 ports = service,
                 detach = True,
                 tty = True,
                 stdin_open = True,
                 privileged = True)

    @staticmethod
    def delete_node(label):
        container = _client_docker.containers.get(label)
        container.stop()
        container.remove()

    @staticmethod
    def node_pause(label):
        container = _client_docker.containers.get(label)
        container.pause()

    @staticmethod
    def node_resume(label):
        container = _client_docker.containers.get(label)
        container.unpause()

    @staticmethod
    def has_node_pid(label):
        container = _client_docker.containers.get(label)
        return container.attrs["State"]["Pid"]

    @staticmethod
    def has_node_ip_management(label):
        container = _client_docker.containers.get(label)
        return  container.attrs['NetworkSettings']['IPAddress']

    @staticmethod
    def has_node_service_exposed_port(label, service_port):
        container = _client_docker.containers.get(label)
        return container.attrs['NetworkSettings']['Ports'][service_port + "/tcp"][0]['HostPort']

    @staticmethod
    def node_send_cmd(label, cmd):
        container = _client_docker.containers.get(name)
        ret = container.exec_run(cmd = cmd, tty = True, privileged = True)

        return ret

