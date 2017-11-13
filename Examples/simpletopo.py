from Link.vethlink import DirectLinkOvsVeth, HostLinkOvsVeth
from Link.link import LinkGroup
from Node.node import NodeGroup
from Node.host import Host
from Node.whitebox import WhiteBox
from log import Logger

#from dataplane import Dataplane


def Topology():
    nodes = NodeGroup()
    links = LinkGroup()

    n1 = WhiteBox(label = "node1")
    n2 = WhiteBox(label = "node2")

    nodes.add_node(node = n1)
    nodes.add_node(node = n2)

    h1 = Host(label = "host1")
    h2 = Host(label = "host2")

    nodes.add_node(node = h1)
    nodes.add_node(node = h2)

    n1_n2 = DirectLinkOvsVeth(node_source = n1, node_target = n2)

    links.add_link(n1_n2)

    h1_n1 = HostLinkOvsVeth(node_host = h1, node_target = n1, ip = "192.168.0.1/24")
    h2_n2 = HostLinkOvsVeth(node_host = h2, node_target = n2, ip = "192.168.0.2/24")

    links.add_link(h1_n1)
    links.add_link(h2_n2)

    nodes.commit()
    links.commit()

    return nodes, links


if __name__ == '__main__':

    log = Logger.logger(name = "simpletopo", level = "debug")

    log.info("Creating Topology")

    Topology()

    log.info("Topology initialized")



