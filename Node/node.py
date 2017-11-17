from log import Logger

import docker
import pyroute2

from utils import check_not_null, create_namespace, delete_namespace

_client_docker = docker.from_env()
_client_iproute = pyroute2.IPRoute()


# noinspection PyAttributeOutsideInit
class Node(object):
    logger = Logger.logger("Node")

    def __init__(self, label = None, type = None, service = None, image = None):
        self.label = label
        self.node_type = type
        self.service = service
        self.image = image

    @property
    def image(self):
        return self.__image

    @image.setter
    def image(self, value):
        self.__image = check_not_null(value = value, msg = "the image name cannot be null")

    @property
    def label(self):
        return self.__label

    @label.setter
    def label(self, value):
        self.__label = check_not_null(value = value, msg = "the label node cannot be null")

    @property
    def node_type(self):
        return self.__type

    @node_type.setter
    def node_type(self, value):
        self.__type = check_not_null(value = value, msg = "the type node cannot be null")

    @property
    def control_ip(self):
        try:
            return ApiNode.has_node_ip_management(label = self.label)
        except Exception as ex:
            self.logger.error(ex.args[0])

    @property
    def service_exposed_port(self):
        try:
            return ApiNode.has_node_service_exposed_port(label = self.label, service_port = self.service)
        except Exception as ex:
            self.logger.error(ex.args[0])

    @property
    def node_pid(self):
        try:
            return ApiNode.has_node_pid(label = self.label)
        except Exception as ex:
            self.logger.error(ex.args[0])

    @property
    def node_status(self):
        try:
            return ApiNode.node_status(label = self.label)
        except Exception as ex:
            self.logger.error(ex.args[0])

    def send_cmd(self, cmd = None):
        try:
            return ApiNode.node_send_cmd(self.label, cmd = cmd)
        except Exception as ex:
            self.logger.error(ex.args[0])


class ApiNode(object):
    @staticmethod
    def create_node(label, image, service):
        _client_docker.containers \
            .run(image = image,
                 hostname = label,
                 name = label,
                 ports = service,
                 detach = True,
                 tty = True,
                 stdin_open = True,
                 privileged = True)
        status = ApiNode.node_status(label = label)

        if status == "running":
            pid = ApiNode.has_node_pid(label = label)
            create_namespace(pid = pid)
            return True
        else:
            return False

    @staticmethod
    def delete_node(label):
        container = _client_docker.containers.get(label)
        delete_namespace(ApiNode.has_node_pid(label = label))
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
    def node_status(label):
        container = _client_docker.containers.get(label)
        return container.status

    @staticmethod
    def has_node_pid(label):
        container = _client_docker.containers.get(label)
        return container.attrs["State"]["Pid"]

    @staticmethod
    def has_node_ip_management(label):
        container = _client_docker.containers.get(label)
        return container.attrs['NetworkSettings']['IPAddress']

    @staticmethod
    def has_node_service_exposed_port(label, service_port):

        container = _client_docker.containers.get(label)
        service = service_port

        for k, v in service_port.items():
            service[k] = container.attrs['NetworkSettings']['Ports'][k][0]['HostPort']

        return service

    @staticmethod
    def node_send_cmd(label, cmd):
        container = _client_docker.containers.get(label)
        ret = container.exec_run(cmd = cmd, tty = True, privileged = True)
        return ret


class NodeGroup(object):
    logger = Logger.logger("NodeGroup")

    def __init__(self):
        self.__nodes = {}

    def add_node(self, node):
        label = node.label
        self.__nodes.update({label: node})

    def rem_node(self, label):
        if label in self.__nodes.keys():
            del self.__nodes[label]

    def get_nodes(self):
        return self.__nodes.copy()

    def get_node(self, label):
        if label in self.__nodes.keys():
            return self.__nodes[label]
        else:
            return None

    def commit(self):
        if len(self.__nodes) <= 0:
            raise RuntimeError("there is not node to commit")
        else:
            for k, v in self.__nodes.items():
                self.logger.debug("creating node ({label})".format(label = k))
                v.create()

    def remove(self):
        if len(self.__nodes) <= 0:
            raise RuntimeError("there is not node to commit")
        else:
            for k, v in self.__nodes.items():
                self.logger.debug("removing node ({label})".format(label = k))
                v.delete()
