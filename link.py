import logging
from enum import Enum

from functions import ApiLink, ApiInterface


class TypeLink(Enum):
    Host = "hostLink"
    Switch = "switchLink"


class Link(object):
    def __init__(self, source = None, target = None, type = None):
        self.source = source
        self.target = target
        self.type = type
        self.log = logging.getLogger("link.Link")

    def __str__(self):
        str = {
            "source": self.source,
            "target": self.target,
            "ifSource": self.ifSource,
            "ifTarget": self.ifTarget,
            "type": self.type
        }
        return str

    @property
    def source(self):
        return self.__source

    @source.setter
    def source(self, value):
        if None:
            self.log.error("source must be a node object")
        self.__source = value

    @property
    def target(self):
        return self.__target

    @target.setter
    def target(self, value):
        if None:
            self.log.error("target must be a node object")
        self.__target = value

    @property
    def ifSource(self):
        return self.source + "-" + self.target

    @ifSource.setter
    def ifSource(self, value):
        pass

    @property
    def ifTarget(self):
        return self.target + "-" + self.source

    @ifTarget.setter
    def ifTarget(self, value):
        pass

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
        if value is None:
            raise AttributeError("Type cannot be null")
        self.__type = value


class LinkSwitch(Link):
    def __init__(self, source, target):
        super().__init__(source, target, TypeLink.Switch.value)

    pass


class LinkHost(Link):
    def __init__(self, host, target):
        super().__init__(host, target, TypeLink.Host.value)

    pass


class LinkCommand(object):
    @staticmethod
    def create(link):
        def _sw_create():
            ApiLink.create_link_node(link.source, link.target, link.ifSource, link.ifTarget)
            ApiInterface.add_port_to_bridge(link.source, link.ifSource)
            ApiInterface.add_port_to_bridge(link.target, link.ifTarget)

        def _ht_create():
            ApiLink.create_link_node(link.source, link.target, link.ifSource, link.ifTarget)
            ApiInterface.add_port_to_bridge(link.target, link.ifTarget)

        try:
            if isinstance(link, LinkSwitch):
                _sw_create()
            elif isinstance(link, LinkHost):
                _ht_create()
            else:
                raise ValueError("the link object is unknown")
        except Exception as ex:
            print(ex.args[0])

    @staticmethod
    def delete(link):
        def _sw_delete():
            ApiLink.delete_link_node(link.source, link.target, link.ifSource, link.ifTarget)
            ApiInterface.del_port_from_bridge(link.source, link.ifSource)
            ApiInterface.del_port_from_bridge(link.target, link.ifTarget)

        def _ht_delete():
            ApiLink.delete_link_node(link.source, link.target, link.ifSource, link.ifTarget)
            ApiInterface.del_port_from_bridge(link.target, link.ifTarget)

        try:
            if isinstance(link, LinkSwitch):
                _sw_delete()
            elif isinstance(link, LinkHost):
                _ht_delete()
            else:
                raise ValueError("the link object is unknown")
        except Exception as ex:
            print(ex.args[0])
