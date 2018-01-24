from vsdnemu.api.link.linkapi import LinkFabric
from vsdnemu.api.log.logapi import get_logger
from vsdnemu.api.node.nodeapi import NodeFabric

logger = get_logger(__name__)


class Dataplane(object):

    def __init__(self):
        self.__nodes = NodeFabric()
        self.__links = LinkFabric()

    def add_node(self, node):
        try:
            return self.__nodes.add_node(node = node)
        except Exception as ex:
            logger.error(str(ex.args[0]))

    def del_node(self, name):
        try:
            self.__nodes.del_node(name = name)
        except Exception as ex:
            logger.error(str(ex.args[0]))

    def add_link(self, link):
        try:
            return self.__links.add_link(link = link)
        except Exception as ex:
            logger.error(ex.args[0])

    def del_link(self, name):
        if self.__links.is_exist(name = name):
            try:
                self.__links.del_link(name = name)
            except Exception as ex:
                logger.error(ex.args[0])
        else:
            logger.warning("the link was not found")

    def get_node(self, name):
        return self.__nodes.get_node(name = name)

    def get_link(self, name):
        return self.__links.get_link(name = name)

    def get_nodes(self):
        return self.__nodes.get_nodes()

    def get_links(self):
        return self.__links.get_links()

    def exist_node(self, name):
        return self.__nodes.is_exist(name = name)

    def exist_link(self, name):
        return self.__links.is_exist(name = name)

    def commit(self):

        def add_nodes():
            for key, node in self.__nodes.get_nodes().items():
                logger.info("Creating node ({key}:{name}) ".format(name = node.name, key = key))
                node.create()

        def add_links():
            for key, link in self.__links.get_links().items():
                logger.info("Creating link ({key}:{name})".format(name = link.name, key = key))
                s, t = link.create()
                self.__nodes.update_node(idx = s.idx, node = s)
                self.__nodes.update_node(idx = t.idx, node = t)

        add_nodes()
        add_links()

    def delete(self):
        def del_links():
            for key, link in self.__links.get_links().items():
                logger.info("Deleting link ({key}:{name})".format(name = link.name, key = key))
                link.delete()

        def del_nodes():
            for key, node in self.__nodes.get_nodes().items():
                logger.info("Deleting node ({key}:{name}) ".format(name = node.name, key = key))
                node.delete()

        del_links()
        del_nodes()
