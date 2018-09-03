from uuid import uuid4

from vsdnemul.link import Link
from vsdnemul.node import Node

from vsdnemul.lib import iproutelib as iproute

MTU_DEFAULT=9000

def _create_veth():
    source = "veth{id}".format(id=str(uuid4())[:6])
    target = "veth{id}".format(id=str(uuid4())[:6])
    if iproute.create_pair(ifname=source, peer=target,mtu=MTU_DEFAULT):
        return source,target
    return None

def _create_bridge(slaves=None):
    bridge = "br{id}".format(id=str(uuid4())[:6])
    if iproute.create_bridge(ifname=bridge,slaves=slaves, mtu=MTU_DEFAULT):
        return bridge
    return None

def _add_port_br(ifname, bridge):
    return iproute.bridge_add_port(master=bridge, slaves=[ifname])


def _create_link():
    bridge = _create_bridge()
    source = ""
    target = ""

    def _add_link():
        port_node, port_bridge = _create_veth()

        if _add_port_br(ifname=port_bridge,bridge=bridge):
            return port_node
        return None

    source = _add_link()
    target = _add_link()

    return source, target


class Bridge(Link):

    def __init__(self, node_source:Node, node_target: Node):
        super().__init__(node_source, node_target)

    def _commit(self):

        try:
            self.source.add_port(



    def _destroy(self):
        pass


