

from Api.Utils import check_not_null, create_namespace, delete_namespace
from log import Logger

logger = Logger.logger("Node")


class Node(object):
    logger = Logger.logger("Node")

    def __init__(self, label, type = None, service = None, image = None, volume = None, cap_add = None):
        self.__label = label
        self.__type = type
        self.__service = service
        self.__image = image
        self.__volume = volume
        self.__cap_add = cap_add

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
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
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
            return ApiNode.has_node_service_exposed_port(label = self.label, service_port = self.__service)
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

    def get_cli_prompt(self):
        try:
            ApiNode.get_node_prompt(label = self.label)
        except Exception as ex:
            self.logger.error(str(ex.args))

    @property
    def volume(self):
        return self.__volume

    @volume.setter
    def volume(self, value):
        self.__volume = value


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
