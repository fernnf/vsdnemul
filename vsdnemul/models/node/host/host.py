import logging

from vsdnemul.lib import dockerlib as docker
from vsdnemul.node import Node, NodeType
from vsdnemul.models.port.ethernet import Ethernet

logger = logging.getLogger(__name__)



class Host(Node):
    def __init__(self, name, **config):
        config.update(volume = {"/sys/fs/cgroup": {"bind": "/sys/fs/cgroup", "mode": "ro"}})
        config.update(cap_add = ["ALL"])
        super(Host, self).__init__(name=name, image="vsdn/host", type=NodeType.HOST,**config)

    def add_port(self, ip=None, mask=None):
        port = Ethernet(mac=None, ip=ip, mask=mask)
        super().__ports.add_port(port)

    def del_port(self, id):
        try:
            super().del_port(id=id)
        except Exception as ex:
            logger.error(ex.__cause__)

    def get_port(self, id):
        return super().get_port(id=id)

    def commit(self):
        try:
            docker.create_node(name=self.name, image=self.image, **self.config)
            logger.info("the new host ({name}) node was created".format(name=self.name))
        except Exception  as ex:
            logger.error(ex.__cause__)

    def destroy(self):
        try:
            docker.delete_node(name=self.name)
            logger.info("the host ({name}) node was deleted".format(name=self.name))
        except Exception as ex:
            logger.error(ex.__cause__)