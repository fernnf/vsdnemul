from node import WhiteBox, NodeCommand
from link import LinkSwitch, LinkCommand


def create_nodes(nodes=[]):
    for n in nodes:
        NodeCommand.create(n)
        print("new node {node} has created".format(node=n.name))

    for n in nodes:
        NodeCommand.setController(n, "10.126.1.231", "6653")
        print("node {node} has set to controller".format(node = n.name))


def create_links(links=[]):

    for l in links:
        LinkCommand.create(l)
        print("new link created between source {src} to destination {dst}".format(src = l.source, dst = l.target))


def delete_node(nodes=[]):

    for n in nodes:
        NodeCommand.delete(n)


def delete_links(links=[]):
    for l in links:
        LinkCommand.delete(l)

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

    delete_node(nodes)
    #create_nodes(nodes)

    delete_links(links)
    #create_links(links)

    print("Topology initialized")

