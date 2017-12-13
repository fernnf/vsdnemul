from api.utils import check_not_null, create_namespace, delete_namespace
from api.docker.dockerapi import DockerApi
from log import Logger

logger = Logger.logger("node")


class Node(object):

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
    def service_exposed(self):
        try:
            return DockerApi.services_node(name = self.label)
        except Exception as ex:
            logger.error(ex.args[0])

    @property
    def node_pid(self):
        try:
            return DockerApi.get_pid_node(name = self.label)
        except Exception as ex:
            logger.error(ex.args[0])

    @property
    def node_status(self):
        try:
            return DockerApi.get_status_node(name = self.label)
        except Exception as ex:
            logger.error(ex.args[0])

    def send_cmd(self, cmd = None):
        try:
            return DockerApi.run_cmd(name = self.label, cmd = cmd)
        except Exception as ex:
            logger.error(ex.args[0])

    def get_cli_prompt(self, shell = "bash"):
        try:
            DockerApi.get_shell(name = self.label, shell = shell)
        except Exception as ex:
            logger.error(str(ex.args))

    @property
    def volume(self):
        return self.__volume

    @volume.setter
    def volume(self, value):
        self.__volume = value
