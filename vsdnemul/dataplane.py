import logging

from vsdnemul.link import LinkFabric
from vsdnemul.node import NodeFabric

logger = logging.getLogger(__name__)


class Dataplane(object):

    def __init__(self):
        self.__nodes = NodeFabric()
        self.__links = LinkFabric()

    def addNode(self, node):
        try:
            return self.__nodes.addNode(node=node)
        except Exception as ex:
            logger.error(ex.args[0])

    def delNode(self, name):
        try:
            self.__nodes.delNode(name)
        except Exception as ex:
            logger.error(ex.args[0])

    def addLink(self, link):
        try:
            return self.__links.addLink(link)
        except Exception as ex:
            logger.error(ex.args[0])

    def delLink(self, name):

        try:
            self.__links.delLink(name)
        except Exception as ex:
            logger.error(ex.args[0])

    def getNode(self, name):
        return self.__nodes.getNode(name)

    def getNodeId(self, name):
        for n in self.__nodes.getNodes().values():
            if n.getName().__eq__(name):
                return n.getId()
        return self.__nodes.getNode(name).getId()

    def getLink(self, name):
        return self.__links.getLink(name)

    def getNodes(self):
        return self.__nodes.getNodes()

    def getLinks(self):
        return self.__links.getLinks()

    def getCountNodes(self):
        return self.__nodes.getNodes().__len__()

    def getCountLinks(self):
        return self.__links.getLinks().__len__()


    def stop(self):
        def destroyLinks():
            for key,link in self.__links.getLinks().items():
                logger.info("Deleting link ({key}:{name})".format(name=link.getName(), key=link.getId()))
                link._Destroy()

        def destroyNodes():
            for key,node in self.__nodes.getNodes().items():
                logger.info("Deleting node ({key}:{name}) ".format(name=node.getName(), key=node.getId()))
                node._Destroy()
        try:
            if self.getCountLinks() > 0:
                destroyLinks()
            else:
                logger.warning("no links to destroy")

            if self.getCountNodes() > 0:
                destroyNodes()
            else:
                logger.warning("no links to destroy")

        except Exception as ex:
            logger.error(ex.args[0])
