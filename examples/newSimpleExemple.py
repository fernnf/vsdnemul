from vsdnemul.dataplane import Dataplane
from vsdnemul.lib.log import get_logger
from vsdnemul.link import LinkType
from vsdnemul.models.link.linkpair import LinkPair
from vsdnemul.models.node.host.host import Host
from vsdnemul.models.node.switch.whitebox import Whitebox
from vsdnemul.models.node.controller.onos import Onos


def Topology():

    dp = Dataplane()

    sw1 = dp.addNode(Whitebox(name="sw1"))
    print(sw1.getControlAddr())

    #h1 = dp.addNode(Host(name="h1", ip="192.168.0.1", mask="24"))
    #print(h1.getControlAddr())

    #h2 = dp.addNode(Host(name="h2", ip="192.168.0.2", mask="24"))
    #print(h2.getControlAddr())

    #l1 = dp.addLink(LinkPair(name="l1", node_source=sw1, node_target=h1, type=LinkType.HOST))
    #l2 = dp.addLink(LinkPair(name="l2", node_source=sw1, node_target=h2, type=LinkType.HOST))

    return dp


def ControlPlane(dp):

    ctl = dp.addNode(Onos(name="ctl1"))
    mgnt = ctl.getIpController()

    for sw in dp.getNodes().values():
        if sw.getType().describe().__eq__("switch"):
            sw.setController(target=["tcp:{ip}:6640".format(ip=mgnt)], bridge="br_oper0")

    dp.addNode(ctl)

    return dp
if __name__ == '__main__':

    logger = get_logger(__name__)

    dp = Topology()

    #dp = ControlPlane(dp=dp)

    dp.stop()



