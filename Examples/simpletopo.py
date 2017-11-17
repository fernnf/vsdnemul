from Link.vethlink import DirectLinkOvsVeth, HostLinkOvsVeth
from Link.link import LinkGroup
from Node.node import NodeGroup
from Node.host import Host
from Node.whitebox import WhiteBox
from Command.command import Prompt
from log import Logger

from Node.onos import Onos

#from dataplane import Dataplane

_nodes = NodeGroup()
_links = LinkGroup()


def Topology():

    n1 = WhiteBox(label = "node1")
    n2 = WhiteBox(label = "node2")

    _nodes.add_node(node = n1)
    _nodes.add_node(node = n2)

    h1 = Host(label = "host1")
    h2 = Host(label = "host2")

    _nodes.add_node(node = h1)
    _nodes.add_node(node = h2)

    ctl = Onos(label = "ctl1")

    _nodes.add_node(ctl)

    n1_n2 = DirectLinkOvsVeth(node_source = n1, node_target = n2)

    _links.add_link(n1_n2)

    h1_n1 = HostLinkOvsVeth(node_host = h1, node_target = n1, ip = "192.168.0.1/24")
    h2_n2 = HostLinkOvsVeth(node_host = h2, node_target = n2, ip = "192.168.0.2/24")

    _links.add_link(h1_n1)
    _links.add_link(h2_n2)

    _nodes.commit()
    _links.commit()


def Controller():

    ctl = None

    def exist_ctl():
        for k, node in _nodes.get_nodes().items():
            if isinstance(Onos, node):
                ctl = node

    def set_controller():
        for k, node in _nodes.get_nodes().items():
            if isinstance(WhiteBox, node):
                node.set_controller(ip = ctl.control_ip)

    exist_ctl()
    set_controller()

    log.info("Controller IP: {ip}".format(ip=ctl.control_ip))


if __name__ == '__main__':

    log = Logger.logger(name = "simpletopo", level = "debug")

    log.info("Creating Topology")

    Topology()

    Controller()

    log.info("Topology initialized")

    cmd = Prompt(links = _links, nodes = _nodes)
    cmd.cmdloop()




