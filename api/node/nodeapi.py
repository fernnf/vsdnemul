from api.utils import check_not_null, create_namespace, delete_namespace
from api.docker.dockerapi import DockerApi
from log import Logger

logger = Logger.logger("Node")


class Node(object):

    def __init__(self, name, image, type = None, service = None, volume = None, cap_add = None):
        check_not_null(value = name, msg = "the label node cannot be null")
        check_not_null(value = image, msg = "the image name cannot be null")

        self.__name = name
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
            self.name = value

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
        self.__type = value

    @property
    def service_exposed(self):
        try:
            return DockerApi.services_node(name = self.name)
        except Exception as ex:
            logger.error(ex.args[0])

    @property
    def node_pid(self):
        try:
            return DockerApi.get_pid_node(name = self.name)
        except Exception as ex:
            logger.error(ex.args[0])

    @property
    def node_status(self):
        try:
            return DockerApi.get_status_node(name = self.name)
        except Exception as ex:
            logger.error(ex.args[0])

    def send_cmd(self, cmd = None):
        try:
            return DockerApi.run_cmd(name = self.name, cmd = cmd)
        except Exception as ex:
            logger.error(ex.args[0])

    def get_cli_prompt(self, shell = "bash"):
        try:
            DockerApi.get_shell(name = self.name, shell = shell)
        except Exception as ex:
            logger.error(str(ex.args[0]))

    @property
    def volume(self):
        return self.__volume

    @volume.setter
    def volume(self, value):
        pass

    @property
    def cap_add(self):
        return self.__cap_add

    @cap_add.setter
    def cap_add(self, value):
        pass