from vsdnemul.lib.docker import DockerApi
from vsdnemul.log import get_logger
from vsdnemul.node import Node, NodeType

logger = get_logger(__name__)


class Host(Node):

    def __init__(self, name = None):
        super().__init__(name = name,
                         type = NodeType.HOST,
                         image = "vsdn/host",
                         volume = {"/sys/fs/cgroup": {"bind": "/sys/fs/cgroup", "mode": "ro"}},
                         cap_add = ["ALL"])

    def create(self):
        ret = DockerApi.create_node(name = self.name, ports = self.services, volumes = self.volume,
                                    cap_add = self.cap_add, image = self.image)
        if ret is not True:
            logger.error("the node ({name}) cannot be created".format(name = self.name))

    def delete(self):
        ret = DockerApi.delete_node(name = self.name)
        if ret is not True:
            logger.error("the node ({name}) cannot be deleted".format(name = self.name))
