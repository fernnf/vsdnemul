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

    def delNode(self, id):
        try:
            self.__nodes.delNode(id=id)
        except Exception as ex:
            logger.error(ex.args[0])

    def addLink(self, link):
        try:
            return self.__links.addLink(link)
        except Exception as ex:
            logger.error(ex.args[0])

    def delLink(self, id):

        try:
            self.__links.delLink(id=id)
        except Exception as ex:
            logger.error(ex.args[0])

    def getNode(self, id):
        return self.__nodes.getNode(id=id)

    def getNodeId(self, name):
        for n in self.__nodes.getNodes().values():
            if n.name.__eq__(name):
                return n.id
        return None

    def getLink(self, id):
        return self.__links.getLink(id=id)

    def getNodes(self):
        return self.__nodes.getNodes()

    def getLinks(self):
        return self.__links.getLinks()

    def start(self):

        def commitNodes():
            for key, node in self.__nodes.getNodes().items():
                logger.info("Creating node ({key}:{name}) ".format(name=node.name, key=key))
                node._commit()

        def commitLinks():
            for key, link in self.__links.getLinks().items():
                logger.info("Creating link ({key}:{name})".format(name=link.name, key=key))
                s, t = link._commit()
                self.__nodes.update_node(idx=s.idx, node=s)
                self.__nodes.update_node(idx=t.idx, node=t)

        try:
            commitNodes()
            commitLinks()
        except Exception as ex:
            logger.error(ex.args[0])

    def stop(self):
        def destroyLinks():
            for link in self.__links.getLinks().values():
                logger.info("Deleting link ({key}:{name})".format(name=link.name, key=key))
                link._destroy()

        def destroyNodes():
            for node in self.__nodes.getNodes().values():
                logger.info("Deleting node ({key}:{name}) ".format(name=node.name, key=key))
                node._destroy()
        try:
            destroyLinks()
            destroyNodes()
        except Exception as ex:
            logger.error(ex.args[0])
