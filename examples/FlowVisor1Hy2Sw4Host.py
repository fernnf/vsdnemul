#  Copyright @2018
#
#  GERCOM - Federal University of Pará - Brazil
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import time

from vsdnemul.lib.log import get_logger
from vsdnemul.dataplane import Dataplane
from vsdnemul.models.node.switch.whitebox import Whitebox
from vsdnemul.models.node.host.host import Host
from vsdnemul.models.link.linkpair import LinkPair, LinkType
from vsdnemul.models.node.hypervisor.flowvisor import FlowVisor
from vsdnemul.models.node.controller.onos import Onos
from vsdnemul.cli import Cli

if __name__ == '__main__':

    logger = get_logger(__name__)

    # Creating dataplane

    dp = Dataplane()

    # adding nodes

    # Switches
    sw1 = dp.addNode(Whitebox(name="sw1", dpid="0000000000000001", ofversion="OpenFlow10"))
    sw2 = dp.addNode(Whitebox(name="sw2", dpid="0000000000000002", ofversion="OpenFlow10"))

    #Host
    h1 = dp.addNode(Host(name="h1"))
    h2 = dp.addNode(Host(name="h2"))
    h3 = dp.addNode(Host(name="h3"))
    h4 = dp.addNode(Host(name="h4"))

    hr1 = dp.addNode(FlowVisor(name="hr1"))

    ctl = dp.addNode(Onos(name="ctl1"))

    #Links

    lh1 = dp.addLink(LinkPair(name="lh1", node_source=sw1, node_target=h1, type=LinkType.HOST)) #port:1
    lh2 = dp.addLink(LinkPair(name="lh2", node_source=sw1, node_target=h2, type=LinkType.HOST)) #port:2
    lh3 = dp.addLink(LinkPair(name="lh3", node_source=sw2, node_target=h3, type=LinkType.HOST)) #port:1
    lh4 = dp.addLink(LinkPair(name="lh4", node_source=sw2, node_target=h4, type=LinkType.HOST)) #port:2

    l1 = dp.addLink(LinkPair(name="l1", node_source=sw1, node_target=sw2, type=LinkType.DIRECT)) #port:3


    # Conneting to hypervisor

    mngt_hyper = "tcp:{ip}:6633".format(ip=hr1.getControlIp())
    mngt_ctl = "tcp:{ip}:6653".format(ip=ctl.getIpController())

    sw1.setController(target=mngt_hyper, bridge="br_oper0")
    sw2.setController(target=mngt_hyper, bridge="br_oper0")

    hr1.setSlice(name="slice1", ctl_url=mngt_ctl)
    hr1.setFlowSpace(name="sw1", dpid="0000000000000001", prio=10, slice="slice1", match="dl_vlan=20", slice_perm=7)
    hr1.setFlowSpace(name="sw2", dpid="0000000000000002", prio=10, slice="slice1", match="dl_vlan=20", slice_perm=7)

    cli = Cli(dp)
    cli.cmdloop()

    dp.stop()