import argparse
import json
from node import WhiteBox, NodeCommand
from link import LinkSwitch, LinkCommand


if __name__ == '__main__':

    nodes = list()

    n1 = WhiteBox(name = "node1")
    n2 = WhiteBox(name = "node2")
    n3 = WhiteBox(name = "node3")

    nodes.append(n1)
    nodes.append(n2)
    nodes.append(n3)

    links = list()

    l1 = LinkSwitch(source = n1.name, target = n2.name)
    l2 = LinkSwitch(source = n1.name, target = n3.name)

    links.append(l1)
    links.append(l2)

    """
    
    for n in nodes:
        NodeCommand.create(n)
        NodeCommand.setController(n, "10.126.1.231", "6653")
        print("Node ([{}) has created".format(n))

    for l in links:
        LinkCommand.create(l)
        print("link source {src} to destination {dst}".format(src = l.source , dst = l.target))
    
    for n in nodes:
        NodeCommand.setController(n, "10.126.1.231", "6653")

    """
    for l in links:
        LinkCommand.delete(l)
        
    
    for n in nodes:
        #NodeCommand.setController(n, "10.126.1.231", "6653")
        NodeCommand.delete(n)
