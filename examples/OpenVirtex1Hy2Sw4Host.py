import logging

from vsdnemul.cli import Cli
from vsdnemul.dataplane import Dataplane
from vsdnemul.lib.log import get_logger
from vsdnemul.models.link.linkpair import LinkPair, LinkType
from vsdnemul.models.node.controller.onos import Onos
from vsdnemul.models.node.host.host import Host
from vsdnemul.models.node.hypervisor.openvirtex import OpenVirtex
from vsdnemul.models.node.switch.whitebox import Whitebox

if __name__ == '__main__':
    logger = get_logger(__name__)

    # Creating dataplane

    dp = Dataplane()

    # adding nodes

    # Switches
    sw1 = dp.addNode(Whitebox(name="sw1", dpid="0000000000000001", ofversion="OpenFlow10"))
    sw2 = dp.addNode(Whitebox(name="sw2", dpid="0000000000000002", ofversion="OpenFlow10"))

    # Host
    h1 = dp.addNode(Host(name="h1", ip='10.0.0.1', mask="24"))
    h2 = dp.addNode(Host(name="h2"))
    h3 = dp.addNode(Host(name="h3", ip='10.0.0.2', mask="24"))
    h4 = dp.addNode(Host(name="h4"))

    hr1 = dp.addNode(OpenVirtex(name="hr1"))

    ctl = dp.addNode(Onos(name="ctl1"))

    mngt_hyper = "tcp:{ip}:6633".format(ip=hr1.getControlIp())
    mngt_ctl = "tcp:{ip}:6633".format(ip=ctl.getIpController())

    sw1.setController(target=mngt_hyper, bridge="br_oper0")
    sw2.setController(target=mngt_hyper, bridge="br_oper0")

    # Links

    lh1 = dp.addLink(LinkPair(name="lh1", node_source=sw1, node_target=h1, type=LinkType.HOST))  # port:1
    lh2 = dp.addLink(LinkPair(name="lh2", node_source=sw1, node_target=h2, type=LinkType.HOST))  # port:2
    lh3 = dp.addLink(LinkPair(name="lh3", node_source=sw2, node_target=h3, type=LinkType.HOST))  # port:1
    lh4 = dp.addLink(LinkPair(name="lh4", node_source=sw2, node_target=h4, type=LinkType.HOST))  # port:2

    l1 = dp.addLink(LinkPair(name="l1", node_source=sw1, node_target=sw2, type=LinkType.DIRECT))  # port:3


    # Conneting to hypervisor

    def create_virtual_net():

        tnt = hr1.createNetwork(ctl_url=mngt_ctl, net_addr="10.0.0.0", net_mask="24")

        vsw1 = hr1.createSwitch(tenant=tnt, dpids="00:00:00:00:00:00:00:01")
        vsw1port1 = hr1.createPort(tenant=tnt, dpid="00:00:00:00:00:00:00:01", port="1")
        vsw1port2 = hr1.createPort(tenant=tnt, dpid="00:00:00:00:00:00:00:01", port="3")

        vsw2 = hr1.createSwitch(tenant=tnt, dpids="00:00:00:00:00:00:00:02")
        vsw2port1 = hr1.createPort(tenant=tnt, dpid="00:00:00:00:00:00:00:02", port="1")
        vsw2port2 = hr1.createPort(tenant=tnt, dpid="00:00:00:00:00:00:00:02", port="3")

        link = hr1.connectLink(tenant=tnt, src_vdpid=vsw1, src_vport=vsw1port2, dst_vdpid=vsw2, dst_vport=vsw2port2,
                               algo="spf", bkp="1")

        h1mac1 = h1.getMacAddress("1")
        h3mac1 = h3.getMacAddress("1")

        hr1.connectHost(tenant=tnt, vdpid=vsw1, vport=vsw1port1, mac=h1mac1)
        hr1.connectHost(tenant=tnt, vdpid=vsw2, vport=vsw2port1, mac=h3mac1)

        hr1.startNetwork(tenant=tnt)

        if hr1.startSwitch(tnt, vsw1):
            hr1.startPort(tnt, vsw1, vsw1port1)
            hr1.startPort(tnt, vsw1, vsw1port2)
        else:
            logging.info("Cannot start switch")

        if hr1.startSwitch(tnt, vsw2):
            hr1.startPort(tnt, vsw2, vsw2port1)
            hr1.startPort(tnt, vsw2, vsw2port2)
        else:
            logging.info("Cannot start switch")

    status = False

    while not status:
        if hr1.checkSwitchConnected():
            create_virtual_net()
            status = True

    cli = Cli(dp)
    cli.cmdloop()

    dp.stop()
