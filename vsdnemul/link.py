import argparse
from abc import ABC, abstractmethod
from enum import Enum
from uuid import uuid4 as rand_id
from terminaltables import AsciiTable

import cmd2

from cmd2 import with_category, with_argparser

CAT_LINK_MANAGER = "Link Emulation Command"


class LinkType(Enum):
    DIRECT = "direct"
    HOST = "host"
    VIRTUAL = "virtual"
    WIFI = "wifi"

    def describe(self):
        return self.name.lower()

    def typeName(self):
        return self.value

    @classmethod
    def is_member(cls, value):
        return any(value == item.value for item in cls)


class LinkEncap(Enum):
    ETHERNET = "vif"
    OPTICAL = "vopt"
    RADIO = "vwifi"

    def describe(self):
        return self.name.lower()

    def portName(self):
        return self.value

    @classmethod
    def is_member(cls, value):
        return any(value.value == item.value for item in cls)


class Link(ABC):
    __encap__ = ""

    def __init__(self, name, node_source, node_target, type: LinkType, encap: LinkEncap):
        super(Link, self).__init__()
        self.__name = name
        self.__source = node_source
        self.__target = node_target
        self.__type = type
        self.__encap = encap
        self.__id = str(rand_id())
        self.__port_source = None
        self.__port_target = None

    def getName(self):
        return self.__name

    def getIfName(self):
        return "link{id}".format(id=self.__id[:8])

    def getType(self):
        return self.__type

    def getEncap(self):
        return self.__encap

    def getId(self):
        return self.__id

    def getSource(self):
        return self.__source

    def getTarget(self):
        return self.__target

    def getPortSource(self):
        return self.__port_source

    def setPortSource(self, source: int):
        self.__port_source = source

    def getPortTarget(self):
        return self.__port_target

    def setPortTarget(self, target: int):
        self.__port_target = target

    @abstractmethod
    def _Commit(self):
        pass

    @abstractmethod
    def _Destroy(self):
        pass

    def __dict__(self):
        return {
            "id": "{id}".format(id=self.getId()),
            "name": "{name}".format(name=self.getName()),
            "type": "{type}".format(type=self.getType()),
            "encap": "{encap}".format(encap=self.getEncap()),
            "node_source": "{node_src}".format(node_src=self.getSource()),
            "node_target": "{node_tgt}".format(node_tgt=self.getTarget()),
            "port_source": "{port_src}".format(port_src=self.getPortSource()),
            "port_target": "{port_tgt}".format(port_tgt=self.getTarget()),
        }


class LinkFabric(object):
    def __init__(self):
        self.__links = {}

    def isExist(self, name):
        return name in self.__links

    # FIXME: To create search method more opitmized
    def isExistLink(self, source, target):
        src = any(l.getSource() == source or l.getTarget() == source for l in self.__links.values())
        tgt = any(l.getSource() == target or l.getTarget() == target for l in self.__links.values())

        return src and tgt

    def addLink(self, link):
        key = link.getName()

        if self.isExist(key):
            raise ValueError("the link object already exists")

        elif self.isExistLink(link.getSource(), link.getTarget()):
            raise ValueError("the link object already exists")
        else:
            link._Commit()
            self.__links.update({key: link})

    def delLink(self, name):
        if self.isExist(name):
            link = self.__links[name]
            link._Destroy()
            del (self.__links[name])
        else:
            ValueError("the node not found")

    def getLinks(self):
        return self.__links

    def getLink(self, name):
        if self.isExist(name):
            return self.__links[name]
        else:
            ValueError("the link was not found")


class CliLink(cmd2.Cmd):

    def __init__(self, dataplane=None):
        super(CliLink, self).__init__()
        self.dp = dataplane

    list_parser = argparse.ArgumentParser()
    list_parser.add_argument('-a', '--all', action='store_true', dest="all", help='display all nodes from emulation')
    list_parser.add_argument('-i', '--id', action="store", dest="id",
                             help="retrieve all information from specific node")
    list_parser.set_defaults(all=False)
    list_parser.set_defaults(id=None)

    @with_category(CAT_LINK_MANAGER)
    @with_argparser(list_parser)
    def do_list(self, opts):
        """Manager link options of the emulation"""

        def print_data(link):
            data = []
            self.poutput(msg="")
            cid = ["ID", "{id}".format(id=link.getId())]
            data.append(cid)
            name = ["Name", "{name}".format(name=link.getName())]
            data.append(name)
            type = ["Type", "{type}".format(type=link.getType().describe())]
            data.append(type)
            encap = ["Encapsulation","{encap}".format(encap=link.getEncap().describe())]
            data.append(encap)
            source = ["Source", "{src}".format(src=link.getSource().getName())]
            data.append(source)
            target = ["Target", "{tgt}".format(tgt=link.getTarget().getName())]
            data.append(target)

            tables = AsciiTable(data, title="Link: {name}".format(name=link.getName()))
            tables.justify_columns[2] = 'right'

            self.poutput(msg=tables.table)
            self.poutput(msg="")

        def list_all():
            links = self.dp.getLinks()

            for n in links.values():
                print_data(link=n)

        if opts.id is not None:
            try:
                link = self.dp.getNode(opts.id)
                print_data(link=link)
            except:
                self.perror("the link not exists")
        elif opts.all:
            list_all()
        else:
            self.perror("option unknown")



    def do_exit(self, s):
        return True

