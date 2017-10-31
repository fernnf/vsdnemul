from node import WhiteBox, NodeGroup
from link import DirectLinkOvsVeth, HostLinkOvsVeth, LinkGroup
#from dataplane import Dataplane

import time

if __name__ == '__main__':

    nodes = NodeGroup()

    n1 = WhiteBox(label = "node1")
    n2 = WhiteBox(label = "node2")
    #n3 = WhiteBox(label = "node3")

    #h1 = Host(label = "h1", ip = "192.168.0.1", mask = "255.255.255.0")
    #h2 = Host(label = "h2", ip = "192.168.0.2", mask = "255.255.255.0")

    nodes.add_node(node = n1)
    nodes.add_node(node = n2)
    #nodes.add_node(node = n3)


    links = LinkGroup()

    l1 = DirectLinkOvsVeth(node_source = n1 , node_target = n2)
    #l2 = DirectLinkOvsVeth(node_source = n2 , node_target = n3)

    #lh1 = LinkHost(host = h1.label, target = n1.label, ip = h1.ip, mask = h1.mask)
    #lh2 = LinkHost(host = h2.label, target = n3.label, ip = h2.ip, mask = h2.mask)

    links.add_link(link = l1)
    #links.add_link(link = l2)

    #dp = Dataplane(nodes = nodes, links = links)

    #dp.run()

    #dp.set_controller(ip = "10.126.1.231")

    print("Creating Nodes")
    nodes.commit()
    print("Creating Links")
    links.commit()


    print("Topology initialized")

    #time.sleep(60)

    #dp.stop()

    #print("Topology deleted")

