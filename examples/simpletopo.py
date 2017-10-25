from node import WhiteBox, NodeCommand, Host
from link import LinkSwitch, LinkCommand, LinkHost
from dataplane import Dataplane

import time

if __name__ == '__main__':

    nodes = list()

    n1 = WhiteBox(label = "node1")
    n2 = WhiteBox(label = "node2")
    n3 = WhiteBox(label = "node3")

    h1 = Host(label = "h1", ip = "192.168.0.1", mask = "255.255.255.0")
    h2 = Host(label = "h2", ip = "192.168.0.2", mask = "255.255.255.0")

    nodes.append(h1)
    nodes.append(h2)
    nodes.append(n1)
    nodes.append(n2)
    nodes.append(n3)


    links = list()

    l1 = LinkSwitch(source = n1.label, target = n2.label)
    l2 = LinkSwitch(source = n1.label, target = n3.label)

    lh1 = LinkHost(host = h1.label, target = n1.label, ip = h1.ip, mask = h1.mask)
    lh2 = LinkHost(host = h2.label, target = n3.label, ip = h2.ip, mask = h2.mask)

    links.append(l1)
    links.append(l2)
    links.append(lh1)
    links.append(lh2)

    dp = Dataplane(nodes = nodes, links = links)

    dp.run()

    dp.set_controller(ip = "10.126.1.231")

    print("Topology initialized")

    #time.sleep(60)

    #dp.stop()

    #print("Topology deleted")

