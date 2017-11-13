from Node.node import Node, ApiNode
from log import Logger

class Host(Node):

    logger = Logger.logger("Host")

    def __init__(self, label = None,):
        super().__init__(label = label, type = "Host", service = {'22/tcp': None}, image = "vsdn/host")

    def create(self):
        try:
            ApiNode.create_node(label = self.label, image = self.image, service = self.service)
        except Exception as ex:
            self.logger.error(ex.args[0])

    def delete(self):
        try:
            ApiNode.delete_node(self.label)
        except Exception as ex:
            self.logger.error(ex.args[0])
