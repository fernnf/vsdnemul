from vsdnagent.api.dataplane.dataplaneapi import Dataplane
from vsdnagent.api.log.logapi import get_logger
from vsdnagent.api.node.nodeapi import NodeType
from vsdnagent.frontend.cli import Prompt
from vsdnagent.link.veth_link import HostLinkVeth, DirectLinkVeth
from vsdnagent.node.host_node import Host
from vsdnagent.node.onos_node import Onos
from vsdnagent.node.whitebox_node import WhiteBox

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

    data.add_link(link1)
    data.add_link(link2)
    data.add_link(link3)
    data.add_node(n1)
    data.add_node(n2)
    data.add_node(h1)
    data.add_node(h2)
    data.add_node(ctl1)

    return data


def Controlplane(dataplane):
    def exist_ctl():
        for k, n in dataplane.get_nodes().items():
            if n.type == NodeType.CONTROLLER:
                return n
        return None

    def connect_ctl(control_ip):
        if ctl is not None:
            for k, n in dataplane.get_nodes().items():
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



