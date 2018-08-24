import logging


from vsdnemul.link import LinkFabric
from vsdnemul.node import NodeFabric

logger = logging.getLogger(__name__)


class Dataplane(object):

    def __init__(self):
        self.__nodes = NodeFabric()
        self.__links = LinkFabric()

    def add_node(self, node):
        try:
            return self.__nodes.add_node(node = node)
        except Exception as ex:
            logger.error(ex.__cause__)

    def del_node(self, id):
        try:
            self.__nodes.del_node(id=id)
        except Exception as ex:
            logger.error(ex.__cause__)

    def add_link(self, link):
        try:
            return self.__links.add_link(link = link)
        except Exception as ex:
            logger.error(ex.__cause__)

    def del_link(self, name):
        if self.__links.is_exist(name = name):
            try:
                self.__links.del_link(name = name)
            except Exception as ex:
                logger.error(ex.__cause__)
        else:
            logger.warning("the link was not found")

    def get_node(self, id):
        return self.__nodes.get_node(id=id)

    def get_node_id(self, name):
        for n in self.__nodes.get_nodes().values():
            if n.name.__eq__(name):
                return n.id
        return None

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

    def start(self):

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

    def stop(self):
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
