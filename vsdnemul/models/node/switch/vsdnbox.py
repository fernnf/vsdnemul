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

import logging

from vsdnemul.lib import dockerlib as docker
from vsdnemul.lib import iproutelib as iproute
from vsdnemul.lib import ovsdblib as ovsdb
from vsdnemul.node import Node, NodeType

logger = logging.getLogger(__name__)


def _check_ovs(node):
    cmd = "/usr/bin/ovs-vsctl get Open_vSwitch . external_ids:system-id"
    try:
        ret, output = docker.run_cmd(name=node, cmd=cmd)
        if ret == 0:
            return True
        else:
            return False
    except Exception as ex:
        return False


def _set_manager(node, target: list):
    def command():
        cmd = "/usr/bin/ovs-vsctl set-manager"
        if len(target) < 0:
            raise ValueError("the target cannot be null")
        for t in target:
            cmd = cmd + " " + t
        return cmd

    docker.run_cmd(name=node, cmd=command())


def _del_manager(node):
    cmd = "/usr/bin/ovs-vsctl del-manager"
    docker.run_cmd(name=node, cmd=cmd)


def _set_ofversion(db_addr, protocols, bridge):
    table = ["Bridge"]
    args = [bridge, "protocols={version}".format(version=protocols)]
    ovsdb.set_ovsdb(db_addr=db_addr, table=table, value=args)


def _set_controller(bridge, target, db_addr):
    try:
        ovsdb.set_bridge_controller(name=bridge, db_addr=db_addr, target_addr=target)
    except Exception as ex:
        raise RuntimeError(ex.args[0])


def _del_controller(bridge, db_addr):
    try:
        ovsdb.del_bridge_controller(name=bridge, db_addr=db_addr)
    except Exception as ex:
        raise RuntimeError(ex.args[0])


def _get_ip(node):
    return iproute.get_interface_addr(ifname="eth0", netns=node)


def _get_service_addr(node):
    return "tcp:{ip}:6640".format(ip=_get_ip(node))


def _set_bridge(bridge, db_addr, protocols: list = None, datapath_id=None):
    try:
        ovsdb.add_bridge(name=bridge, db_addr=db_addr, protocols=protocols, datapath_id=datapath_id)
    except Exception as ex:
        raise RuntimeError(ex.args[0])


def _del_bridge(bridge, db_addr):
    try:
        ovsdb.rem_bridge(name=bridge, db_addr=db_addr)
    except Exception as ex:
        raise RuntimeError(ex.args[0])


def _get_bridge_dpid(db_addr, bridge):
    table = ["Bridge"]
    value = [bridge, "datapath_id"]
    return ovsdb.get_ovsdb(db_addr=db_addr, table=table, value=value)


def _set_bridge_dpid(db_addr, bridge, dpid):
    table = ["Bridge"]
    value = [bridge, "other_config:datapath-id={dpid}".format(dpid=dpid)]
    ovsdb.set_ovsdb(db_addr=db_addr, table=table, value=value)


def _run_throughput_test(node, name, loop, num_macs, output):
    cmd = "python3 /root/benchtraffic.py -g true -l {l} -c {nm} -m 1 -n {n} -o {o}"
    json = docker.run_cmd(name=node, cmd=cmd.format(l=loop, nm=num_macs, n=name, o=output))
    return json


def _run_latency_test(node, name, loop, num_macs, output):
    cmd = "python3 /root/benchtraffic.py -g true -l {l} -c {nm} -m 0 -n {n} -o {o}"
    json = docker.run_cmd(name=node, cmd=cmd.format(l=loop, nm=num_macs, n=name, o=output))
    return json


class VSDNBox(Node):
    __environment__ = ["container=docker"]
    __image__ = "vsdn/vsdnbox"
    __type__ = NodeType.SWITCH
    __volumes__ = {"/sys/fs/cgroup": {"bind": "/sys/fs/cgroup", "mode": "ro"},
                   "/root/results": {"bind": "/root/results", "mode": "rw"}}
    __cap_add__ = ["ALL"]

    def __init__(self, name, orches_ip, dpid=None, ofversion=None, bridge="tswitch0", type=NodeType.SWITCH):
        super().__init__(name=name, image=self.__image__, type=type)
        self.__environment__.append("ORCH_ADDR=ws://{}:8080/ws".format(orches_ip))
        self.brdfl = bridge
        self.dpid = dpid
        self.ofversion = ofversion

        self.config.update(environment=self.__environment__)
        self.config.update(cap_add=self.__cap_add__)
        self.config.update(volumes=self.__volumes__)

    @classmethod
    def commit(cls, name, bridge="tswitch0"):
        node = cls(name, bridge)
        node._Commit()
        return node

    def get_bridge_oper(self):
        return self.brdfl

    def get_control_uri(self):
        try:
            return _get_service_addr(self.getName())
        except Exception as ex:
            logger.error(ex.args[0])
            return None

    def get_dpid(self, bridge="tswitch0"):
        try:
            return _get_bridge_dpid(db_addr=self.get_control_uri(), bridge=bridge)
        except Exception as ex:
            logger.error(ex.args[0])
            return None

    def set_dpid(self, dpid, bridge="br_oper0"):
        try:
            _set_bridge_dpid(db_addr=self.get_control_uri(), bridge=bridge, dpid=dpid)
        except Exception as ex:
            logger.error(ex.args[0])

    def set_manager(self, target: list = None):
        try:
            _set_manager(node=self.getName(), target=target)
        except Exception as ex:
            logger.error(ex.args[0])

    def del_manager(self):
        try:
            _del_manager(node=self.getName())
        except Exception as ex:
            logger.error(ex.args[0])

    def set_controller(self, target, bridge="tswitch0"):
        try:
            _set_controller(db_addr=self.get_control_uri(), target=target, bridge=bridge)
        except Exception as ex:
            logger.error(ex.args[0])

    def del_controller(self, bridge="tswitch0"):
        try:
            _del_controller(bridge=bridge, db_addr=self.get_control_uri())
        except Exception as ex:
            logger.error(ex.args[0])

    def set_bridge(self, bridge, protocols: list = None, datapath_id=None):
        try:
            _set_bridge(bridge=bridge, db_addr=self.get_control_uri(), protocols=protocols, datapath_id=datapath_id)
        except Exception as ex:
            logger.error(ex.args[0])

    def del_bridge(self, bridge):
        try:
            _del_bridge(bridge, db_addr=self.get_control_uri())
        except Exception as ex:
            logger.error(ex.args[0])

    def set_ofversion(self, bridge="tswitch0", protocols: list = None):
        try:
            _set_ofversion(db_addr=self.get_control_uri(), protocols=protocols, bridge=bridge)
        except Exception as ex:
            logger.error(ex.args[0])

    def run_command(self, cmd):
        try:
            return docker.run_cmd(name=self.getName(), cmd=cmd)
        except Exception as ex:
            raise RuntimeError(str(ex))

    def setInterface(self, ifname, encap):

        idx = str(self.count_interface.__next__())
        interface = encap.portName() + idx
        try:
            iproute.add_port_ns(ifname=ifname, netns=self.getName(), new_name=interface)
            ovsdb.add_port_bridge(db_addr=self.get_control_uri(), name=self.get_control_uri(), port_name=interface,
                                  ofport=idx)
            self.interfaces.update({idx: interface})
            return idx
        except Exception as ex:
            logger.error(str(ex))

    def delInterface(self, idx):
        interface = self.interfaces[idx]
        try:
            ovsdb.del_port_bridge(db_addr=self.get_control_uri(), name=self.get_control_uri(), port_name=interface)
            iproute.delete_port(ifname=interface, netns=self.getName())
            del (self.interfaces[idx])
        except Exception as ex:
            logger.error(ex.args[0])

    def run_throughput_test(self, name, loop, num_macs, output):
        try:
            import json
            j = _run_throughput_test(self.getName(), name=name, loop=loop, num_macs=num_macs, output=output)
            ret = json.loads(j)
            return ret
        except Exception as ex:
            logger.error(str(ex))

    def _Commit(self):

        def create_node():
            ret = docker.create_node(name=self.getName(), image=self.getImage(), **self.config)
            logger.info("the new whitebox ({name}) node was created".format(name=self.getName()))
            return ret

        def check_ovs():
            try:
                ret = ovsdb.get_ovsdb(db_addr=self.get_control_uri(), table=['Open_vSwitch'],
                                      value=['.', 'external_ids'])
                logger.info("Openvswitch {} enabled ".format(ret[0]['system-id']))
            except Exception as ex:
                check_ovs()

        def config_node():
            logger.info("configuring node")
            self.set_bridge(bridge=self.get_bridge_oper())
            if self.dpid is not None:
                self.set_dpid(bridge=self.get_bridge_oper(), dpid=self.dpid)
            if self.ofversion is not None:
                self.set_ofversion(bridge=self.get_bridge_oper(), protocols=self.ofversion)

            self.set_controller(target="tcp:127.0.0.1:6653", bridge="tswitch0")
            logger.info("done")

        try:
            ret = create_node()
            if ret:
                check_ovs()
                config_node()
            else:
                logger.error("cannot create node")
        except Exception as ex:
            logger.error(str(ex))

    def _Destroy(self):
        try:
            docker.delete_node(name=self.getName())
            logger.info("the whitebox ({name}) node was deleted".format(name=self.getName()))
        except Exception as ex:
            logger.error(str(ex))
