from link import LinkCommand, LinkHost
from node import NodeCommand, ApiNode


class Dataplane(object):
    def __init__(self, nodes = list(), links = list()):
        self._nodes = nodes
        self._links = links

    def set_controller(self, ip, port = "6653"):

        for n in self._nodes:
            if ApiNode.nodeGetStatus(name = n.name) == "running":
                if not isinstance(n, LinkHost):
                    NodeCommand.setController(n, ip = ip, port = port)
                    print("node {node} has set to controller".format(node = n.name))
            else:
                raise RuntimeError("the nodes is not initialized")

    def run(self):
        for n in self._nodes:
            NodeCommand.create(n)
            print("new node {node} has created".format(node = n.name))

        for l in self._links:
            LinkCommand.create(l)
            print("new link created between source {src} to destination {dst}".format(src = l.node_source, dst = l.node_target))

    def stop(self):
        for l in self._links:
            LinkCommand.delete(l)
            print("the link between {source} and {target} has deleted from topology".format(source = l.node_source,
                                                                                            target = l.node_target))

        for n in self._nodes:
            NodeCommand.delete(n)
            print("the node {node} has deleted from topology".format(node = n.name))
