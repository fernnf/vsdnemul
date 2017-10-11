from node import WhiteBox, NodeCommand, Host
from link import LinkSwitch, LinkCommand, LinkHost
from dataplane import Dataplane

import time

if __name__ == '__main__':

    nodes = list()

    n1 = WhiteBox(name = "node1")
    n2 = WhiteBox(name = "node2")
    n3 = WhiteBox(name = "node3")

    h1 = Host(name = "h1", ip ="192.168.0.1", mask = "255.255.255.0")
    h2 = Host(name = "h2", ip ="192.168.0.2", mask = "255.255.255.0")

    nodes.append(h1)
    nodes.append(h2)
    nodes.append(n1)
    nodes.append(n2)
    nodes.append(n3)


    links = list()

    l1 = LinkSwitch(source = n1.name, target = n2.name)
    l2 = LinkSwitch(source = n1.name, target = n3.name)

    lh1 = LinkHost(host = h1.name, target = n1.name, ip = h1.ip, mask = h1.mask)
    lh2 = LinkHost(host = h2.name, target = n3.name, ip = h2.ip, mask = h2.mask)

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

