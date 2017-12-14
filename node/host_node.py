from api.log.logapi import get_logger
from api.node.nodeapi import Node
from api.docker.dockerapi import DockerApi

logger = get_logger("Host")


class Host(Node):

    def __init__(self, name = None):
        super().__init__(name = name, type = "host-node",image = "vsdn/host", volume = None,
                         cap_add = ["SYS_ADMIN", "NET_ADMIN"])

    def create(self):
        ret = DockerApi.create_node(name = self.name, ports = self.service_exposed, volumes = self.volume,
                                    cap_app = self.cap_add, image = self.image)
        if ret is not True:
            logger.error("the node ({name}) cannot be created".format(name = self.name))

    def delete(self):
        ret = DockerApi.delete_node(name = self.name)
        if ret is not True:
            logger.error("the node ({name}) cannot be deleted".format(name = self.name))