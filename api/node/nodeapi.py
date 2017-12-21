from api.utils import check_not_null, create_namespace, delete_namespace
from api.docker.dockerapi import DockerApi
from api.port.portapi import Port , PortFabric
from log import Logger
from enum import Enum

logger = Logger.logger("Node")


class NodeType(Enum):
    HOST = 1
    SWITCH = 2
    ROUTER = 3
    WIFI_ROUTER = 4
    VIRTUAL_SWITCH = 5

    def describe(self):
        return self.name.lower()

    @classmethod
    def has_member(cls, value):
        return any(value == item.value for item in cls)


class Node(object):

    def __init__(self, name, image, type: NodeType, idx = None, services = None, volume = None, cap_add = None):
        check_not_null(value = name, msg = "the label node cannot be null")
        check_not_null(value = image, msg = "the image name cannot be null")

        self.__name = name
        self.__type = type
        self.__services = services
        self.__image = image
        self.__volume = volume
        self.__cap_add = cap_add
        self.__ports = []
        self.__idx = idx

    @property
    def image(self):
        return self.__image

    @image.setter
    def image(self, value):
        pass

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        if DockerApi.get_status_node(self.name) == "running":
            DockerApi.rename_node(self.name, new_name = value)
            self.__name = value
        else:
            self.__name = value

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
        if NodeType.has_member(value = value):
            self.__type = value

    @property
    def services(self):
        return self.__services

    @property
    def volume(self):
        return self.__volume

    @volume.setter
    def volume(self, value):
        if self.__volume is None:
            self.__volume = value
        else:
            pass

    @property
    def cap_add(self):
        return self.__cap_add

    @cap_add.setter
    def cap_add(self, value):
        if self.__cap_add is None:
            self.__cap_add =  value
        else:
            pass

    @services.setter
    def services(self, value):
        if self.__services is None:
            self.__services = value
        else:
            pass

    @property
    def node_pid(self):
        try:
            return DockerApi.get_pid_node(name = self.name)
        except Exception as ex:
            logger.error(str(ex.args[0]))

    @property
    def node_status(self):
        try:
            return DockerApi.get_status_node(name = self.name)
        except Exception as ex:
            logger.error(str(ex.args[0]))

    @property
    def idx(self):
        return self.__idx

    @idx.setter
    def idx(self, value):
        if self.__idx is None:
            self.__idx = value
        else:
            pass

    def send_cmd(self, cmd = None):
        try:
            return DockerApi.run_cmd(name = self.name, cmd = cmd)
        except Exception as ex:
            logger.error(str(ex.args[0]))

    def get_cli_prompt(self, shell = "bash"):
        try:
            DockerApi.get_shell(name = self.name, shell = shell)
        except Exception as ex:
            logger.error(str(ex.args[0]))

    def add_port(self, port_name):
        try:
            self.__ports.append(port_name)
        except Exception as ex:
            logger.error(str(ex.args[0]))

    def del_port(self, name ):
        try:
            self.__ports.remove(name)
        except Exception as ex:
            logger.error(str(ex.args[0]))

    def get_ports(self):
        return self.__ports.copy()