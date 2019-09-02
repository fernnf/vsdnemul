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

from vsdnemul.lib.log import get_logger
from vsdnemul.dataplane import Dataplane
from vsdnemul.lib.log import get_logger
from vsdnemul.link import LinkType
from vsdnemul.models.link.linkpair import LinkPair
from vsdnemul.models.node.host.host import Host
from vsdnemul.models.node.switch.vsdnbox import VSDNBox
from vsdnemul.models.node.hypervisor.vsdnorches import VSDNOrches
from vsdnemul.models.node.controller.onos import Onos
from vsdnemul.cli import Cli


if __name__ == '__main__':
    logger = get_logger(__name__)
    dp = Dataplane()
    orch = dp.addNode(VSDNOrches("orch"))
    ip_orch = orch.getControlIp()
    for i in range(1, 16):
        dp.addNode(VSDNBox(name="sw{}".format(i), orches_ip=ip_orch, dpid="000000000000000{}".format(i), ofversion=["OpenFlow13"]))

    cli = Cli(dp)
    cli.cmdloop()

    dp.stop()

