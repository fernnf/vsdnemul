import uuid

from api.node.nodeapi import Node
from api.utils import check_not_null


class Link(object):

    def __init__(self, type, node_source: Node, node_target: Node):
        self.__node_source = node_source
        self.__node_target = node_target
        self.__type = type
        self.__id = str(uuid.uuid4())[0:8]

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, value):
        pass

    @property
    def node_source(self):
        return self.__node_source

    @node_source.setter
    def node_source(self, value):
        self.__node_source = check_not_null(value = value, msg = "the label of source node cannot be null")

    @property
    def node_target(self):
        return self.__node_target

    @node_target.setter
    def node_target(self, value):
        self.__node_target = check_not_null(value = value, msg = "the label of target node cannot be null")

    @property
    def port_source(self):
        return self.__node_source.name + "-" + self.__node_target.name

    @port_source.setter
    def port_source(self, value):
        pass

    @property
    def port_target(self):
        return self.__node_target.name + "-" + self.__node_source.name

    @port_target.setter
    def port_target(self, value):
        pass

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
        self.__type = check_not_null(value = value, msg = "type of link cannot be null")


"""
class LinkGroup(object):

    logger = Logger.logger("LinkGroup")

    def __init__(self):
        self.__links = {}

    def add_link(self, link):
        label = link.id
        self.__links.update({label: link})

    def rem_link(self, link):
        link.delete()
        del self.__links[link.id]

    def get_links(self):
        return self.__links.copy()

    def get_link(self, id):
        return self.__links[id]

    def commit(self):
        if len(self.__links) <= 0:
            raise RuntimeError("there is not link to commit")
        else:
            for k, v in self.__links.items():
                self.logger.info("creating link {key} from {a} to {b}".format(key= k, a = v.port_source, b= v.port_target))
                v.create()

    def remove(self):
        if len(self.__links) <= 0:
            raise RuntimeError("there is not node to commit")
        else:
            for k, v in self.__links.items():
                self.logger.info("removing link ({label})".format(label = k))
                v.delete()
"""
