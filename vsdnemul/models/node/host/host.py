import logging

from vsdnemul.lib import dockerlib as docker
from vsdnemul.models.port.ethernet import Ethernet
from vsdnemul.node import Node, NodeType

logger = logging.getLogger(__name__)


class Host(Node):

    __volumes__ = {"/sys/fs/cgroup": {"bind": "/sys/fs/cgroup", "mode": "ro"}}
    __cap_add__ = ["ALL"]
    __images__ = "vsdn/host"
    __type__ = NodeType.HOST

    def __init__(self, name, **config):
        config.update(volumes=self.__volumes__)
        config.update(cap_add=self.__cap_add__)
        super(Host, self).__init__(name=name, image= self.__images__, type=self.__type__, **config)

    def add_port(self, ip=None, mask=None):
        port = Ethernet(mac=None, ip=ip, mask=mask)
        try:
            self._ports.add_port(port)
        except Exception as ex:
            logger.error(ex.args[0])

    def del_port(self, id):
        try:
            self._ports.del_port(id=id)
        except Exception as ex:
            logger.error(ex.args[0])

    def get_port(self, id):
        try:
            return self._ports.get_port(id=id)
        except Exception as ex:
            logger.error(ex.args[0])
            return None

    def _commit(self):
        try:
            docker.create_node(name=self.name, image=self.image, **self.config)
            logger.info("the new host ({name}) node was created".format(name=self.name))
        except Exception  as ex:
            logger.error(ex.args[0])

    def _destroy(self):
        try:
            docker.delete_node(name=self.name)
            logger.info("the host ({name}) node was deleted".format(name=self.name))
        except Exception as ex:
            logger.error(ex.args[0])
