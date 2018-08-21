from vsdnemul.lib.docker import DockerApi
from vsdnemul.log import get_logger
from vsdnemul.node import Node, NodeType
from vsdnemul.node import NodeTemplate

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


class Host(NodeTemplate):

    def __init__(self, name, image):

        super(Host, self).__init__(name=name, image=image, **kwargs)

    def create(self):
        pass

    def delete(self):
        pass