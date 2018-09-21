import logging
import traceback
from enum import Enum
import time

from vsdnemul.lib import dockerlib as docker
from vsdnemul.lib import iproutelib as iproute
from vsdnemul.lib import ovsdblib as ovsdb
from vsdnemul.node import Node, NodeType

logger = logging.getLogger(__name__)

"""Begin self API for special commands"""

def _SetManager(node, target: list):
    def command():
        cmd = "/usr/bin/ovs-vsctl set-manager"
        if len(target) < 0:
            raise ValueError("the target cannot be null")
        for t in target:
            cmd = cmd + " " + t
        return cmd

    docker.run_cmd(name=node, cmd=command())


def _DelManager(node):
    cmd = "/usr/bin/ovs-vsctl del-manager"
    docker.run_cmd(name=node, cmd=cmd)


def _SetOpenflowVersion(db_addr, protocols: list, bridge):
    table = ["Bridge"]
    args = [bridge, "protocols={version}".format(version=protocols)]
    ovsdb.set_ovsdb(db_addr=db_addr, table=table, value=args)


def _SetController(bridge, target: list, db_addr):
    try:
        ovsdb.set_bridge_controller(name=bridge, db_addr=db_addr, target_addr=target)
    except Exception as ex:
        raise RuntimeError(ex.args[0])


def _DelController(bridge, db_addr):
    try:
        ovsdb.del_bridge_controller(name=bridge, db_addr=db_addr)
    except Exception as ex:
        raise RuntimeError(ex.args[0])


def _GetManagerAddr(node):
    def get_ip():
        return iproute.get_interface_addr(ifname="eth0", netns=node)

    return "tcp:{ip}:6640".format(ip=get_ip())


def _GetManagerIP(node):
    return iproute.get_interface_addr(ifname="eth0", netns=node)


def _SetBridge(bridge, db_addr, protocols: list = None, datapath_id=None):
    try:
        ovsdb.add_bridge(name=bridge, db_addr=db_addr, protocols=protocols, datapath_id=datapath_id)
    except Exception as ex:
        raise RuntimeError(ex.args[0])


def _DelBridge(bridge, db_addr):
    try:
        ovsdb.rem_bridge(name=bridge, db_addr=db_addr)
    except Exception as ex:
        raise RuntimeError(ex.args[0])


""" End self API"""


class OfVersion(Enum):
    OF_10 = "OpenFlow10"
    OF_13 = "OpenFlow13"
    OF_14 = "OpenFlow14"


class Whitebox(Node):
    __cap_add__ = ["ALL"]
    __image__ = "vsdn/whitebox"
    __type__ = NodeType.SWITCH
    __volumes__ = {"/sys/fs/cgroup": {"bind": "/sys/fs/cgroup", "mode": "ro"}}
    __ports__ = None

    def __init__(self, name, bridge_oper="br_oper0"):
        super(Whitebox, self).__init__(name, image=self.__image__, type=self.__type__)
        self.config.update(volumes=self.__volumes__)
        self.config.update(cap_add=self.__cap_add__)
        self.config.update(ports=self.__ports__)

        self.__br_oper = bridge_oper

    @classmethod
    def commit(cls, name, bridge_oper="br_oper0"):
        node = cls(name, bridge_oper)
        node._Commit()
        return node

    def getBrOper(self):
        return self.__br_oper

    def getControlAddr(self):
        try:
            return _GetManagerAddr(self.getName())
        except Exception as ex:
            logger.error(ex.args[0])
            return None

    def setManager(self, target: list = None):
        try:
            _SetManager(node=self.getName(), target=target)
        except Exception as ex:
            logger.error(ex.args[0])

    def delManager(self):
        try:
            _DelManager(node=self.getName())
        except Exception as ex:
            logger.error(ex.args[0])

    def setController(self, target: list = None, bridge="br_oper0"):
        try:
            _SetController(db_addr=self.getControlAddr(), target=target, bridge=bridge)
        except Exception as ex:
            logger.error(ex.args[0])

    def delController(self, bridge="br_oper0"):
        try:
            _DelController(bridge=bridge, db_addr=self.getControlAddr())
        except Exception as ex:
            logger.error(ex.args[0])

    def setBridge(self, bridge, protocols: list = None, datapath_id=None):
        try:
            _SetBridge(bridge=bridge, db_addr=self.getControlAddr(), protocols=protocols, datapath_id=datapath_id)
        except Exception as ex:
            logger.error(ex.args[0])

    def delBridge(self, bridge):
        try:
            _DelBridge(bridge, db_addr=self.getControlAddr())
        except Exception as ex:
            logger.error(ex.args[0])

    def setOpenflowVersion(self, bridge="br_oper0", protocols: list = None):
        try:
            _SetOpenflowVersion(db_addr=self.getControlAddr(), protocols=protocols, bridge=bridge)
        except Exception as ex:
            logger.error(ex.args[0])

    def setInterface(self, ifname, encap):
        idx = str(self.count_interface.__next__())
        interface = encap.portName() + idx
        try:
            iproute.add_port_ns(ifname=ifname, netns=self.getName(), new_name=interface)
            ovsdb.add_port_bridge(db_addr=self.getControlAddr(), name=self.getBrOper(), port_name=interface,
                                  ofport=idx)
            self.interfaces.update({idx: interface})
            return idx
        except Exception as ex:
            logger.error(ex.args[0])

    def delInterface(self, idx):

        interface = self.interfaces[idx]

        try:
            ovsdb.del_port_bridge(db_addr=self.getControlAddr(), name=self.getBrOper(), port_name=interface)
            iproute.delete_port(ifname=interface, netns=self.getName())
            del (self.interfaces[idx])
        except Exception as ex:
            logger.error(ex.args[0])

    def _Commit(self):
        try:
            if docker.create_node(name=self.getName(), image=self.getImage(), **self.config):
                logger.info("the new whitebox ({name}) node was created".format(name=self.getName()))
                if self.getStatus().__eq__("running"):
                    logger.info("setting whitebox configuration")
                    # We need that openvswitch process already has stared
                    time.sleep(3)
                    self.setManager(target=["ptcp:6640"])
                    self.setBridge(bridge=self.getBrOper())

                else:
                    logger.warning("the node is not running")

        except Exception as ex:
            logger.error(ex.args[0])

    def _Destroy(self):
        try:
            docker.delete_node(name=self.getName())
            logger.info("the whitebox ({name}) node was deleted".format(name=self.getName()))
        except Exception as ex:
            traceback.print_exc()
            logger.error(ex.args[0])
