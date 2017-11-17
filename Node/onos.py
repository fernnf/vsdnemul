from Node.node import Node, ApiNode
from log import Logger


class Onos(Node):
    logger = Logger.logger("ONOS")

    def __init__(self, label = None):
        super(Onos, self).__init__(label = label,
                                   type = "ONOS Controller",
                                   service = {'6653/tcp': None, '6640/tcp': None, '8181/tcp': None, '8101/tcp': None,
                                              '9876/tcp': None},
                                   image = "onosproject/onos")

    def create(self):
        try:
            return ApiNode.create_node(label = self.label, image = self.image, service = self.service)
        except Exception as ex:
            self.logger.error(ex.args[0])

    def delete(self):
        try:
            return ApiNode.delete_node(label = self.label)
        except Exception as ex:
            self.logger.error(str(ex.args))