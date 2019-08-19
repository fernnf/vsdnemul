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

from IPython import embed

import logging

if __name__ == '__main__':
    logger = get_logger(__name__)

    dp = Dataplane()

    # Adding SDN Switch
    sw1 = dp.addNode(Whitebox(name="sw1", bridge_oper="tswitch0", dpid="0000000000000001", ofversion="OpenFlow13"))
    sw2 = dp.addNode(Whitebox(name="sw2", bridge_oper="tswitch0", dpid="0000000000000002", ofversion="OpenFlow13"))

    # Adding Two Hosts Clientscl
    h1 = dp.addNode(Host(name="h1", ip="10.0.0.1", mask="24"))

    h2 = dp.addNode(Host(name="h2", ip="10.0.0.2", mask="24"))

    # Creating Link Connection
    # Link Between h1 to sw1
    l1 = dp.addLink(LinkPair(name="l1", node_source=sw1, node_target=h1, type=LinkType.HOST))
    # Link Between h2 to sw2
    l2 = dp.addLink(LinkPair(name="l2", node_source=sw2, node_target=h2, type=LinkType.HOST))
    # Link Between sw1 to sw2
    l3 = dp.addLink(LinkPair(name="l3", node_source=sw1, node_target=sw2, type=LinkType.DIRECT))
    # Creating a SDN Controller and setting to switch
    ctl = dp.addNode(Onos(name="ctl1"))
    ctl1 = "tcp:{ip}:6653".format(ip="172.17.0.1")
    ctl2 = "tcp:{ip}:6654".format(ip="172.17.0.1")
    sw1.setController(target=ctl1, bridge="tswitch0")
    sw2.setController(target=ctl2, bridge="tswitch0")

    # enabling cli
    cli = Cli(dp)
    cli.cmdloop()
    # embed()
    # destroing all elements after the experiment.
    dp.stop()
