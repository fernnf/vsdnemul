from api.log.logapi import get_logger

logger = get_logger("Dataplane")


class Dataplane(object):

    def __init__(self):
        self.__nodes = {}
        self.__links = {}

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

    def commit(self):

        for key, node in self.__nodes.items():
            logger.info("Creating node {name}".format(name = key))
            node.create()

        for key, link in self.__links.items():
            logger.info("Creating link {name}".format(name = key))
            link.create()

    def delete(self):

        for key, node in self.__nodes.items():
            logger.info("Deleting node {name}".format(name = key))
            node.delete()

        for key, link in self.__links.items():
            logger.info("Deleting link {name}".format(name = key))
            link.delete()
