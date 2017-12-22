from api.log.logapi import get_logger
from api.port.portapi import Port, PortFabric
from port.veth_port import SwitchEthPort, HostEthPort
from api.node.nodeapi import NodeFabric
from api.link.linkapi import LinkFabric, LinkType
from itertools import count

logger = get_logger("Dataplane")


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
            self.del_link(name = name)
        except Exception as ex:
            logger.error(str(ex.args[0]))

    def add_link(self, link):
        if not self.__links.is_exist(link.name):
            node_target =  self.__nodes.

            if link.type is LinkType.DIRECT:

    def del_link(self, name):
        for k,v in self.__links.items():
            if v.name.__eq__(name):
                del self.__links[v.idx]
                return True
        return False

    def get_node(self, idx):
        if idx is not None:
            if idx in self.__nodes.keys():
                return self.__nodes[idx]

    def get_link(self, idx):
        if idx is not None:
            if idx in self.__links.keys():
                return self.__links[idx]
        return None

    def get_nodes(self):
        return self.__nodes.copy()

    def get_links(self):
        return self.__links.copy()

    def exist_node(self, idx = None, name = None):
        if idx is not None:
            if idx in self.__nodes.keys():
                return True
        if name is not None:
            for k, v in self.__nodes.items():
                if v.__eq__(name):
                    return True
        return False

    def exist_link(self, idx = None, name = None):
        if idx is not None:
            if idx in self.__links.keys():
                return True
        if name is not None:
            for k,v in self.__links.items():
                if v.name.__eq__(name):
                    return True
        return False

    def commit(self):

        def add_nodes():
            for key, node in self.__nodes.items():
                logger.info("Creating node ({name})".format(name = node.name))
                node.create()

        def add_links():

            for key, link in self.__links.items():

                node_source = self.get_node(link.node_source)
                node_target = self.get_node(link.node_target)

                port_source = Port()



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

    def __get_next_port(self, node):
        ports = node.get_ports()
        if len(ports) > 0:
            idx = len(ports)+1
            port = Port(idx = idx, )
            return "eth{idx}".format(idx = idx)
