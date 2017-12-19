from api.log.logapi import get_logger

logger = get_logger("Dataplane")


class Dataplane(object):

    def __init__(self):
        self.__nodes = {}
        self.__links = {}
        self.__ports = {}

    def add_node(self, node):
        self.__nodes.update({node.name: node})

    def del_node(self, name):
        del self.__nodes[name]

    def add_link(self, link):
        self.__links.update({link.id: link})

    def del_link(self, id):
        del self.__links[id]

    def get_node(self, name):
        return self.__nodes[name]

    def get_link(self, id):
        return self.__links[id]

    def get_nodes(self):
        return self.__nodes.copy()

    def get_links(self):
        return self.__links.copy()

    def exist_node(self, name):
        for k, v in self.__nodes.items():
            if v.__eq__(name):
                return True
        return False

    def exist_link(self, id = None, source = None, target = None, ):

        if id is not None:
            for k, v in self.__links.items():
                if v.id == id:
                    return True

        if source is not None and target is not None:
            for k, v in self.__links.items():
                if v.node_source == source and v.node_target == target:
                    return True
                elif v.node_source == target and v.node_target == source:
                    return True

        return False

    def commit(self):

        def add_nodes():
            for key, node in self.__nodes.items():
                logger.info("Creating node {name}".format(name = key))
                node.create()

        def add_links():
            for key, link in self.__links.items():
                logger.info("Creating link {name}".format(name = key))
                link.create()

        add_nodes()
        add_links()

    def delete(self):
        def del_links():
            for key, link in self.__links.items():
                logger.info("Deleting link {name}".format(name = key))
                link.delete()

        def del_nodes():
            for key, node in self.__nodes.items():
                logger.info("Deleting node {name}".format(name = key))
                node.delete()

        del_links()
        del_nodes()
