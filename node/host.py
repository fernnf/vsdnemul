from api.utils import
from api.log.logapi import get_logger
from api.node.nodeapi import DockerApi


class Host(Node):
    logger = get_logger("Host")

    def __init__(self, label = None):
        DockerApi.create_node(
        super().__init__(label = label, type = "Host", service = {'22/tcp': None, '5201/tcp': None},
                         image = "vsdn/host", volume = None,
                         cap_add = ["SYS_ADMIN", "NET_ADMIN"])

    def create(self):
        try:
            ApiNode.create_node(label = self.label, image = self.image, service = self.service, volume = self.volume,
                                cap_add = self.cap_add)
        except Exception as ex:
            self.logger.error(str(ex.args))

    def delete(self):
        try:
            ApiNode.delete_node(self.label)
        except Exception as ex:
            self.logger.error(str(ex.args))
