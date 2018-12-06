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

from vsdnemul.dataplane import Dataplane
from vsdnemul.lib.log import get_logger
from vsdnemul.link import LinkType
from vsdnemul.models.link.linkpair import LinkPair
from vsdnemul.models.node.host.host import Host
from vsdnemul.models.node.switch.whitebox import Whitebox
from vsdnemul.models.node.controller.onos import Onos
from vsdnemul.cli import Cli

if __name__ == '__main__':

    logger = get_logger(__name__)

    # Define Dataplane

    dp = Dataplane()

    # Adding nodes to dataplane
    # Create Switch Nodes

    sw1 = dp.addNode(Whitebox("sw1"))
    sw2 = dp.addNode(Whitebox("sw2"))
    sw3 = dp.addNode(Whitebox("sw3"))
    sw4 = dp.addNode(Whitebox("sw4"))
    sw5 = dp.addNode(Whitebox("sw5"))
    sw6 = dp.addNode(Whitebox("sw6"))
    sw7 = dp.addNode(Whitebox("sw7"))
    sw8 = dp.addNode(Whitebox("sw8"))
    sw9 = dp.addNode(Whitebox("sw9"))
    sw10 = dp.addNode(Whitebox("sw10"))

    # Create Host Nodes

    h1 = dp.addNode(Host(name="h1", ip="192.168.0.1", mask="24"))
    h2 = dp.addNode(Host(name="h2", ip="192.168.0.2", mask="24"))

    # Adding links to dataplane

    l1 = dp.addLink(LinkPair(name="l1", node_source=sw1, node_target=sw2, type=LinkType.DIRECT))
    l2 = dp.addLink(LinkPair(name="l2", node_source=sw1, node_target=sw3, type=LinkType.DIRECT))
    l3 = dp.addLink(LinkPair(name="l3", node_source=sw1, node_target=sw4, type=LinkType.DIRECT))
    l4 = dp.addLink(LinkPair(name="l4", node_source=sw2, node_target=sw3, type=LinkType.DIRECT))
    l5 = dp.addLink(LinkPair(name="l5", node_source=sw2, node_target=sw4, type=LinkType.DIRECT))
    l6 = dp.addLink(LinkPair(name="l6", node_source=sw3, node_target=sw4, type=LinkType.DIRECT))
    l7 = dp.addLink(LinkPair(name="l7", node_source=sw4, node_target=sw3, type=LinkType.DIRECT))

    hl1 = dp.addLink(LinkPair(name="hl1", node_source=h1, node_target=sw1, type=LinkType.HOST))
    hl2 = dp.addLink(LinkPair(name="hl2", node_source=h2, node_target=sw4, type=LinkType.HOST))

    # Adding Controller

    ctl = dp.addNode(Onos(name="ctl1"))
    mgnt = "tcp:{ip}:6653".format(ip=ctl.getIpController())

    sw1.setController(target=mgnt, bridge="br_oper0")
    sw2.setController(target=mgnt, bridge="br_oper0")
    sw3.setController(target=mgnt, bridge="br_oper0")
    sw4.setController(target=mgnt, bridge="br_oper0")
    
    # Manager Emulation by CLI
    cli = Cli(dp)
    cli.cmdloop()

    # Stopping Emulation
    dp.stop()
