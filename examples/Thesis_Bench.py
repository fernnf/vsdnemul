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

import json
import logging
import threading
import uuid

from vsdnemul.cli import Cli
from vsdnemul.dataplane import Dataplane
from vsdnemul.lib.log import get_logger
from vsdnemul.models.node.controller.ryuctl import Ryuctl
from vsdnemul.models.node.hypervisor.vsdnorches import VSDNOrches
from vsdnemul.models.node.switch.vsdnbox import VSDNBox
from vsdnemul.node import NodeType

log = logging.getLogger(__name__)


def create_switches_vsdn(dp, n, a):
    for i in range(0, n):
        dp.addNode(VSDNBox(name="sw{}".format(i + 1), orches_ip=a, dpid="000000000000000{}".format(i + 1),
                           ofversion="OpenFlow13"))


def run_throughput(node, name, loop, macs, output):
    cmd = "python3 /root/benchtraffic/benchtraffic.py -l {l} -c {m} -m 1 -n {n} -t {t}"
    ret = node.run_command(cmd=cmd.format(l=loop, m=macs, n=name, t=output))
    log.info("throughput test has finished on {}".format(node.getName()))
    log.info(json.loads(ret[1]))


def run_latency(node, name, loop, macs, output):
    cmd = "python3 /root/benchtraffic/benchtraffic.py -l {l} -c {m} -m 0 -n {n} -t {t}"
    ret = node.run_command(cmd=cmd.format(l=loop, m=macs, n=name, t=output))
    log.info("latency test has finished on {}".format(node.getName()))
    log.info(json.loads(ret[1]))


def run_throughput_test(dp, name, loop, macs, output):
    for a in dp.getNodes().values():
        if a.__type__.name == NodeType.SWITCH.name:
            log.info("initializing throughput test on node {}".format(a.getName()))
            t = threading.Thread(target=run_throughput, args=(a, name + a.getName(), loop, macs, output))
            t.setName(a.getName())
            t.start()
        else:
            log.info("Node is not switch")


def run_latency_test(dp, name, loop, macs, output):
    for a in dp.getNodes().values():
        if a.__type__.name == NodeType.SWITCH.name:
            log.info("initializing latency test on node {}".format(a.getName()))
            t = threading.Thread(target=run_latency, args=(a, name + a.getName(), loop, macs, output))
            t.setName(a.getName())
            t.start()
        else:
            log.info("Node is not switch")


def create_slice_vsdn(dp, ctl):
    def config_patch(n, v, t):
        n.set_port(bridge=v, port="vport1-link1", peer="link1-vport1", patch=True, portnum="1")
        n.set_port(bridge=v, port="vport2-link2", peer="link2-vport2", patch=True, portnum="2")
        n.set_port(bridge=t, port="link1-vport1", peer="vport1-link1", patch=True, portnum="3")
        n.set_port(bridge=t, port="link2-vport2", peer="vport2-link2", patch=True, portnum="4")
        log.info("patch ports configured")

    def config_openflow(n):
        cmd = "/usr/bin/ovs-ofctl -O OpenFlow13 add-flow {b} in_port={p1},actions=output={p2}"
        n.run_command(cmd=cmd.format(b="tswitch0", p1="1", p2="3"))
        n.run_command(cmd=cmd.format(b="tswitch0", p1="3", p2="1"))
        n.run_command(cmd=cmd.format(b="tswitch0", p1="2", p2="4"))
        n.run_command(cmd=cmd.format(b="tswitch0", p1="4", p2="2"))
        log.info("openflows configured")

    def config_dut_port(n, b):
        cmd_veth = "/usr/sbin/ip link add {p1} type veth peer name {p2}"
        cmd_up = "/usr/sbin/ip link set {p1} up"
        n.run_command(cmd=cmd_veth.format(p1="dut1", p2="link1"))
        n.run_command(cmd=cmd_veth.format(p1="dut2", p2="link2"))
        n.run_command(cmd=cmd_up.format(p1="dut1"))
        n.run_command(cmd=cmd_up.format(p1="dut2"))
        n.run_command(cmd=cmd_up.format(p1="link1"))
        n.run_command(cmd=cmd_up.format(p1="link2"))
        n.set_port(bridge=b, port="link1", portnum="1")
        n.set_port(bridge=b, port="link2", portnum="2")
        log.info("dut ports configured")

    for n in dp.getNodes().values():
        if n.__type__.name == NodeType.SWITCH.name:
            id = str(uuid.uuid4()).replace("-", "")
            n.set_bridge(bridge=id[:8], protocols="OpenFlow13", datapath_id=id[:16])
            config_patch(n, v=id[:8], t="tswitch0")
            config_dut_port(n, b="tswitch0")
            config_openflow(n)
            n.set_controller(target=ctl, bridge=id[:8])
        else:
            log.info("Node is not switch")


if __name__ == '__main__':
    logger = get_logger(__name__)
    dp = Dataplane()
    ctl = dp.addNode(Ryuctl("clt"))
    orch = dp.addNode(VSDNOrches("orch"))
    ip_orch = orch.getControlIp()
    ctl_addr = "tcp:{}:6653".format(ctl.getControlIp())

    create_switches_vsdn(dp, 3, ip_orch)
    create_slice_vsdn(dp, ctl=ctl_addr)
    run_throughput_test(dp=dp, loop="5", macs="10000", name="test_3switch_", output="/root/results")

    cli = Cli(dp)
    cli.cmdloop()

    dp.stop()
