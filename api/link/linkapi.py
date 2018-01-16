import uuid
from enum import Enum
from itertools import count

from api.utils.utils import check_not_null


class LinkType(Enum):
    DIRECT = "d"
    HOST = "h"
    VIRTUAL = "v"
    WIFI = "w"

    def describe(self):
        return self.name.lower()

    @classmethod
    def is_member(cls, value):
        return any(value == item.value for item in cls)


class Link(object):

    def __init__(self, node_source, node_target, type: LinkType, idx = None):
        self.__node_source = check_not_null(value = node_source, msg = "the name of source node cannot be null")
        self.__node_target = check_not_null(value = node_target, msg = "the name of target node cannot be null")
        self.__type = check_not_null(value = type, msg = "type of link cannot be null")
        self.__idx = idx



    @property
    def name(self):
        return "{type}{idx}".format(type = self.type.value, idx = self.idx)

    @name.setter
    def name(self, value):
        pass

    @property
    def node_source(self):
        return self.__node_source

    @node_source.setter
    def node_source(self, value):
        pass

    @property
    def node_target(self):
        return self.__node_target

    @node_target.setter
    def node_target(self, value):
        pass

    @property
    def port_source(self):
        return self.__port_source

    @port_source.setter
    def port_source(self, value):
        self.__port_source = value

    @property
    def port_target(self):
        return self.__port_target

    @port_target.setter
    def port_target(self, value):
       self.__port_target = value

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
        if LinkType.is_member(value = value):
            self.__type = value
        else:
            raise ValueError("the type is not member of NodeType")

    @property
    def idx(self):
        return self.__idx

    @idx.setter
    def idx(self, value):
        if self.__idx is None:
            self.__idx = value
        else:
            pass


class LinkFabric(object):
    def __init__(self):
        self.__links = {}
        self.__links_idx = count()

    def add_link(self, link):
        if not self.is_exist(name = link.name):
            key = self.__links_idx.__next__()
            link.idx = key
            self.__links.update({key:link})
            return link
        else:
            raise ValueError("the node object already exists")

    def del_link(self, name = None):
        if self.is_exist(name = name):
            key = self.__get_index(name = name)
            del self.__links[key]
        else:
            ValueError("the node was not found")

    def update_link(self, idx, link):
        if self.is_exist(name = link.name):
            self.__links.update({idx: link})
        else:
            ValueError("the node was not found")

    def get_links(self):
        return self.__links.copy()

    def get_link(self, name):
        check_not_null(name, "the name cannot be null")
        if self.is_exist(name = name):
            key = self.get_index(name = name)
            return self.__links[key]
        else:
            ValueError("the link was not found")

    def is_exist(self, name):
        return self.__exist_link(name = name)

    def get_index(self, name):
        if self.__exist_link(name = name):
            return self.__get_index(name = name)
        else:
            ValueError("the node was not found")

    def __get_index(self, name):
        for k, n in self.__links.items():
            if n.name.__eq__(name):
                return k

    def __exist_link(self, name = None, idx = None):

        if name is not None:
            key = self.__get_index(name = name)
            if key is not None:
                return True

        if idx is not None:
            if idx in self.__links.keys():
                return True

        return False
