import logging
from enum import Enum

from vsdnemul.lib import dockerlib as docker
from vsdnemul.lib import iproutelib as iproute
from vsdnemul.lib import ovsdblib as ovsdb
from vsdnemul.models.port.ethernet import Ethernet
from vsdnemul.node import Node, NodeType
from vsdnemul.port import Port

logger = logging.getLogger(__name__)

"""Begin self API for special commands"""


def _add_port_ns(node, ifname, new_name):
    return iproute.add_port_ns(ifname=ifname, netns=node, new_name=new_name)

def _rem_port_ns(node, ifname):
    return iproute.delete_port(ifname=ifname,netns=node)

def _add_port_ovs(db_addr, br_oper, port_name, ofport):
    ovsdb.add_port_bridge(db_addr=db_addr, name=br_oper, port_name=port_name, ofport=ofport)

def _rem_port_ovs(db_addr, br_oper, port_name):
    ovsdb.del_port_bridge(db_addr=db_addr, name=br_oper, port_name=port_name)

def _set_manager(node, target=None):
    def command():
        cmd = "/usr/bin/ovs-vsctl set-manager"
        for t in target:
            cmd = cmd + " " + t
        return cmd

    default = ["ptcp:6640"]

    if target is not None:
        if not default in target:
            target = target + default
    else:
        target = default

    docker.run_cmd(name=node, cmd=command())


def _set_openflow_version(db_addr, version, bridge):
    table = ["Bridge"]
    args = [bridge, "protocols={version}".format(version=[version])]
    ovsdb.set_ovsdb(db_addr=db_addr, table=table, args=args)


def _get_mngt_addr(node):
    def get_ip():
        return iproute.get_interface_addr(ifname="eth0", netns=node)

    return "tcp:{ip}:6640".format(ip=get_ip())


""" End self API"""


class OF_VERSION(Enum):
    OF_10 = "OpenFlow10"
    OF_13 = "OpenFlow13"
    OF_14 = "OpenFlow14"


class Whitebox(Node):
    __ports__ = None
    __volumes__ = None
    __cap_add__ = ["ALL"]
    __image__ = "vsdn/whitebox"
    __type__ = NodeType.SWITCH

    def __init__(self, name, bridge_oper="br_oper0", **config):
        config.update(ports=self.__ports__)
        config.update(volumes=self.__volumes__)
        config.update(cap_add=self.__cap_add__)
        super(Whitebox, self).__init__(name=name, type=self.__type__, image=self.__image__, **config)
        self.__bridge_oper = bridge_oper

    @property
    def br_oper(self):
        return self.__bridge_oper

    @br_oper.setter
    def br_oper(self, value):
        pass

    @property
    def control_addr(self):
        try:
            return _get_mngt_addr(self.name)
        except Exception as ex:
            logger.error(ex.args[0])
            return None

    @control_addr.setter
    def control_addr(self, value):
        pass

    def set_openflow_version(self, version: list, bridge="br_oper0", ):
        try:
            _set_openflow_version(db_addr=self.control_addr, version=version, bridge=bridge)
        except Exception as ex:
            logger.error(ex.args[0])

    def set_manager(self, target=[]):
        try:
            _set_manager(node=self.name, target=target)
        except Exception as ex:
            logger.error(ex.args[0])

    def set_controller(self, target: list, bridge="br_oper0"):
        try:
            ovsdb.set_bridge_controller(name=bridge, db_addr=self.control_addr, target_addr=target)
        except Exception as ex:
            logger.error(ex.args[0])

    def del_controller(self, bridge="br_oper0"):
        try:
            ovsdb.del_bridge_controller(name=bridge, db_addr=self.control_addr)
        except Exception as ex:
            logger.error(ex.args[0])

    def add_port(self, ifname, port:Port ):
        try:
            key = self._ports.add_port(port=port)
            port = self._ports.get_port(id=key)
            _add_port_ns(node=self.name, ifname=ifname, new_name=port.name)
            _add_port_ovs(db_addr=self.control_addr, br_oper=self.br_oper, port_name=port.name, ofport=key)
            return key
        except Exception as ex:
            logger.error(ex.args[0])

    def del_port(self, id):
        try:
            port = self._ports.get_port(id=id)
            _rem_port_ovs(db_addr=self.control_addr,br_oper=self.br_oper, port_name=port.name)
            _rem_port_ns(node=self.name,ifname=port.name)
            self._ports.del_port(id=id)
        except Exception as ex:
            logger.error(ex.args[0])

    def get_port(self, id):
        try:
            return self._ports.get_port(id=id)
        except Exception as ex:
            logger.error(ex.args[0])
            return None

    def get_len_ports(self):
        return len(self.get_ports)

    def _commit(self):
        try:
            docker.create_node(name=self.name, image=self.image, **self.config)
            self.set_manager()
            ovsdb.add_bridge(name=self.br_oper,
                             db_addr=self.control_addr)
            logger.info("the new whitebox ({name}) node was created".format(name=self.name))
        except Exception  as ex:
            logger.error(ex.args[0])

    def _destroy(self):
        try:
            docker.delete_node(name=self.name)
            logger.info("the whitebox ({name}) node was deleted".format(name=self.name))
        except Exception as ex:
            logger.error(ex.args[0])
