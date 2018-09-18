import argparse
import itertools
import logging
from abc import ABC, abstractmethod
from enum import Enum

import cmd2
from cmd2 import with_argparser, with_category
from terminaltables import AsciiTable


from vsdnemul.lib.dockerlib import get_status_node, get_id, get_control_ip, get_shell

'''
Class Abstract to generate new nodes models based on docker file templates. 
'''

logger = logging.getLogger(__name__)


CAT_NODE_MANAGER = "Node Emulation Command"

class NodeType(Enum):
    HOST = "host"
    SWITCH = "switch"
    ROUTER = "router"
    WIFI_ROUTER = "wifi_router"
    CONTROLLER = "controller"
    SERVER = "server"
    HYPERVISOR = "sdn_hypervisor"

    def describe(self):
        return self.name.lower()

    @classmethod
    def has_member(cls, value):
        return any(value == item.value for item in cls)


class Node(ABC):
    __ports__ = ""
    __volumes__ = ""
    __cap_add__ = ""
    __image__ = ""
    __type__ = ""

    def __init__(self, name, image, type: NodeType):
        super(Node, self).__init__()
        self.__name = name
        self.__type = type
        self.__image = image
        self.__cid = None
        self.config = dict()
        self.interfaces = dict()
        self.count_interface = itertools.count(start=1, step=1)

    def getControlIp(self):
        return get_control_ip(self.__name)

    def getName(self):
        return self.__name

    def getImage(self):
        return self.__image

    def getStatus(self):
        try:
            return get_status_node(self.__name)
        except:
            return None

    def getId(self):
        try:
            return get_id(self.__name)
        except:
            return None

    def getType(self):
        return self.__type

    def setType(self, type: NodeType):
        self.__type = type

    @abstractmethod
    def setInterface(self, ifname, encap):
        pass

    @abstractmethod
    def delInterface(self, id):
        pass

    @abstractmethod
    def _Commit(self):
        pass

    @abstractmethod
    def _Destroy(self):
        pass

    def __dict__(self):
        return {
            "id": self.getId(),
            "name": self.getName(),
            "image": self.getImage(),
            "type": self.getType().name,
            "status": self.getStatus(),
        }

    def __str__(self):
        return [
            "id={id}".format(id=self.getId()),
            "name={name}".format(name=self.getName()),
            "image={image}".format(image=self.getImage()),
            "type={type}".format(type=self.getType().name),
            "status={status}".format(status=self.getStatus())
        ]


class NodeFabric(object):

    def __init__(self):
        self.__nodes = {}

    def isExist(self, name):
        return any(k == name for k in self.__nodes.keys())

    def addNode(self, node):
        key = node.getName()
        if not self.isExist(name=key):
            self.__nodes.update({key: node})
            node._Commit()
            return node
        else:
            raise ValueError("the node already exists".format(name=key))

    def delNode(self, name):
        if self.isExist(name):
            node = self.__nodes[name]
            node._Destroy()
            del self.__nodes[name]
        else:
            raise ValueError("the node not found")

    def getNode(self, name):
        return self.__nodes[name]

    def getNodes(self):
        return self.__nodes


class CliNode(cmd2.Cmd):


    def __init__(self, dataplane=None):
        super(CliNode, self).__init__()
        self.dp = dataplane

    list_parser = argparse.ArgumentParser()
    list_parser.add_argument('-a', '--all', action='store_true', dest="all", help='display all nodes from emulation')
    list_parser.add_argument('-i', '--id', action="store", dest="id",
                             help="retrieve all information from specific node")
    list_parser.set_defaults(all=False)
    list_parser.set_defaults(id=None)

    @with_category(CAT_NODE_MANAGER)
    @with_argparser(list_parser)
    def do_list(self, opts):
        """Manager node options of the emulation"""

        def print_data(node):
            data = []
            self.poutput(msg="")
            cid = ["ID", "{id}".format(id=node.getId())]
            data.append(cid)
            name = ["Name", "{name}".format(name=node.getName())]
            data.append(name)
            type = ["Type", "{type}".format(type=node.getType().describe())]
            data.append(type)
            ipmgt = ["Ip Control", "{ip}".format(ip=node.getControlIp())]
            data.append(ipmgt)
            status = ["Status", "{status}".format(status=node.getStatus())]
            data.append(status)

            tables = AsciiTable(data, title="Node: {name}".format(name=node.getName()))
            tables.justify_columns[2] = 'right'

            self.poutput(msg=tables.table)
            self.poutput(msg="")

        def list_all():
            nodes = self.dp.getNodes()

            for n in nodes.values():
                print_data(node=n)

        if opts.id is not None:
            try:
                node = self.dp.getNode(opts.id)
                print_data(node=node)
            except:
                self.perror("the node not exists")
        elif opts.all:
            list_all()
        else:
            self.perror("option unknown")


    cli_parser =  argparse.ArgumentParser()
    cli_parser.add_argument('-i', '--id', action="store", dest="id", help="get cli prompt from a specific node")
    cli_parser.set_defaults(id=None)
    @with_category(CAT_NODE_MANAGER)
    @with_argparser(cli_parser)
    def do_cli(self, opts):
        """Get a cli prompt from a node of the emulation"""
        try:
            if opts.id is not None:
                get_shell(name=opts.id)
            else:
                self.perror("id option cannot be null")
        except Exception as ex:
            self.perror(ex.args[0])


    def do_exit(self, s):
        return True
