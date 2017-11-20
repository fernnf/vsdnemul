from Node.node import Node, ApiNode
from log import Logger


class Host(Node):

    logger = Logger.logger("Host")

    def __init__(self, label = None):
        super().__init__(label = label, type = "Host", service = {'22/tcp': None}, image = "vsdn/host", volume = None)

    def create(self):
        try:
            ApiNode.create_node(label = self.label, image = self.image, service = self.service, volume = self.volume)
        except Exception as ex:
            self.logger.error(str(ex.args))

    def delete(self):
        try:
            ApiNode.delete_node(self.label)
        except Exception as ex:
            self.logger.error(str(ex.args))
