#!/usr/bin/env python3
from vsdnemul.dataplane import Dataplane
from vsdnemul.lib.log import get_logger
from vsdnemul.node import NodeType
from vsdnemul.cli import Prompt
from vsdnemul.models.link import HostLinkVeth, DirectLinkVeth
from vsdnemul.models.node.host.host_node import Host
from vsdnemul.models.node.controller.onos_node import Onos
from vsdnemul.models.node.switch.whitebox_node import WhiteBox

logger = get_logger("topology.script")


def Topology():

    n1 = WhiteBox(name = "node1")
    n2 = WhiteBox(name = "node2")
    ctl1 = Onos(name = "control1")

    h1 = Host(name = "host1")
    h2 = Host(name = "host2")

    link1 = HostLinkVeth(node_host = h1, node_target = n1, ip_host = "10.0.0.1/24", mtu = "9000")
    link2 = HostLinkVeth(node_host = h2, node_target = n2, ip_host = "10.0.0.2/24", mtu = "9000")
    link3 = DirectLinkVeth(node_source = n1, node_target = n2, mtu = "9000")

    data = Dataplane()

    data.addLink(link1)
    data.addLink(link2)
    data.addLink(link3)
    data.addNode(n1)
    data.addNode(n2)
    data.addNode(h1)
    data.addNode(h2)
    data.addNode(ctl1)

    return data


def Controlplane(dataplane):
    def exist_ctl():
        for k, n in dataplane.getNodes().items():
            if n.type == NodeType.CONTROLLER:
                return n
        return None

    def connect_ctl(control_ip):
        if ctl is not None:
            for k, n in dataplane.getNodes().items():
                if n.type == NodeType.SWITCH:
                    n.set_controller(ip = control_ip)

    ctl = exist_ctl()
    connect_ctl(control_ip = ctl.control_ip)
    logger.info("Controller IP: http://{ip}:8181/onos/ui/login.html".format(ip = ctl.control_ip))



"""
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
"""

if __name__ == '__main__':
    logger.info("Creating Topology")

    data = Topology()

    data.commit()

    logger.info("Topology initialized")

    Controlplane(dataplane = data)

    logger.info("Control plane initialized")

    cmd = Prompt(dataplane = data)
    cmd.cmdloop()



