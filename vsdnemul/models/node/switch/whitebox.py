import logging

from vsdnemul.models.port.ethernet import Ethernet
from vsdnemul.node import Node
from vsdnemul.lib import dockerlib as docker
from vsdnemul.port import Port

logger = logging.getLogger(__name__)

class Whitebox(Node):
    def __init__(self, name, bridge_oper="br_oper0", **config):
        config.update(service=None)
        config.update(volume=None)
        config.update(cap_add=["ALL"])
        super(Whitebox, self).__init__(name=name, image="vsdn/whitebox",**config)
        self.__bridge_oper = bridge_oper

    def add_port(self):
        port = Ethernet()
        super()._ports.add_port(port)

    def del_port(self, id):
        try:
            super().del_port(id=id)
        except Exception as ex:
            logger.error(ex.__cause__)

    def get_port(self, id):
        return super().get_port(id=id)

    def get_len_ports(self):
        return len(super()._ports.get_ids())

    def commit(self):
        try:
            docker.create_node(name=self.name,image=self.image, **self.config)
            logger.info("the new whitebox ({name}) node was created".format(name=self.name))
        except Exception  as ex:
            logger.error(ex.__cause__)

    def destroy(self):
        try:
            docker.delete_node(name=self.name)
            logger.info("the whitebox ({name}) node was deleted".format(name=self.name))
        except Exception as ex:
            logger.error(ex.__cause__)


