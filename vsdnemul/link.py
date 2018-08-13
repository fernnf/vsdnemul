from enum import Enum
from itertools import count
from uuid import uuid4 as rand_id

from vsdnemul.lib.utils import check_not_null


class LinkType(Enum):
    DIRECT = "DIRECT"
    HOST = "HOST"
    VIRTUAL = "VIRTUAL"
    WIFI = "WIFI"

    def describe(self):
        return self.name.lower()

    @classmethod
    def is_member(cls, value):
        return any(value == item.value for item in cls)


class Link(object):

    def __init__(self, node_source, node_target, template, type: LinkType):
        super(Link, self).__init__()
        self.__node_source = node_source
        self.__node_target = node_target
        self.__type = type
        self.__template = template
        self.__id = rand_id()

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, value):
        pass

    @property
    def template(self):
        return self.__template

    @template.setter
    def template(self, value):
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
        return self.__type.describe()

    @type.setter
    def type(self, value):
        if LinkType.is_member(value=value):
            self.__type = value
        else:
            raise ValueError("the type is not member of NodeType")

    def __dict__(self):
        return {
            "id": "{id}".format(id=self.id),
            "object": "{obj}".format(obj=__name__),
            "type": "{type}".format(type=self.type),
            "node_source": "{node_src}".format(node_src=self.node_source),
            "node_target": "{node_tgt}".format(node_tgt=self.node_target),
            "port_source": "{port_src}".format(port_src=self.port_source),
            "port_target": "{port_tgt}".format(port_tgt=self.port_target),
        }


class LinkFabric(object):
    def __init__(self):
        self.__links = {}

    def add_link(self, link):
        if self.is_exist(id=link.id):
            raise ValueError("the node object already exists")
        else:
            key = link.id
            self.__links.update({key: link})


    def del_link(self, id):
        if self.is_exist(id):
            del self.__links[id]
        else:
            ValueError("the node was not found")

    def update_link(self, id, link):
        if not id.__eq__(link.id):
            raise ValueError("Link id and object are different")

        if self.is_exist(id):
            self.__links.update({id: link})
        else:
            ValueError("the node was not found")

    def get_links(self):
        return self.__links.copy()

    def get_link(self, id):
        if self.is_exist(id):
            return self.__links[id]
        else:
            ValueError("the link was not found")

    def is_exist(self, id):
        return id in self.__links
