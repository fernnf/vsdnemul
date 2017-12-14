from link.vethlink import DirectLinkOvsVeth, HostLinkOvsVeth
from link.link import LinkGroup
from node.node import NodeGroup
from node.host_node import Host
from node.whitebox_node import WhiteBox
from Command.command import Prompt
from log import Logger

from node.onos_node import Onos

#from dataplane import Dataplane

_nodes = NodeGroup()
_links = LinkGroup()


def Topology():

    n1 = WhiteBox(label = "node1")
    #n2 = WhiteBox(label = "node2")

    _nodes.add_node(node = n1)
    #_nodes.add_node(node = n2)

    h1 = Host(name = "host1")
    h2 = Host(name = "host2")

    _nodes.add_node(node = h1)
    _nodes.add_node(node = h2)

    ctl = Onos(label = "ctl1")

    _nodes.add_node(ctl)

    #n1_n2 = DirectLinkOvsVeth(node_source = n1, node_target = n2)

    #_links.add_link(n1_n2)

    h1_n1 = HostLinkOvsVeth(node_host = h1, node_target = n1, ip = "192.168.0.1/24")
    h2_n1 = HostLinkOvsVeth(node_host = h2, node_target = n1, ip = "192.168.0.2/24")

    _links.add_link(h1_n1)
    _links.add_link(h2_n1)

    _nodes.commit()
    _links.commit()


def Controller():

    def exist_ctl():
        for k, node in _nodes.get_nodes().items():
            if isinstance(node, Onos):
                return node

    def set_controller(ctl_ip):
        if ctl is not None:
            for k, node in _nodes.get_nodes().items():
                if isinstance(node, WhiteBox):
                    node.set_controller(ip = ctl_ip)
        else:
            log.warn("No controller setting")

    ctl = exist_ctl()
    set_controller(ctl_ip = ctl.control_ip)

    log.info("Controller IP: http://{ip}:8181/onos/ui/login.html".format(ip=ctl.control_ip))


if __name__ == '__main__':

    log = Logger.logger(name = "simpletopo", level = "debug")

    log.info("Creating Topology")

    Topology()

    Controller()

    log.info("Topology initialized")

    cmd = Prompt(links = _links, nodes = _nodes)
    cmd.cmdloop()




