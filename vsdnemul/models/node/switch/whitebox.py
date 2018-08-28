import logging

from vsdnemul.lib import dockerlib as docker
from vsdnemul.lib import ovsdblib as ovsdb
from vsdnemul.lib import iproutelib as iproute
from vsdnemul.models.port.ethernet import Ethernet
from vsdnemul.node import Node, NodeType

logger = logging.getLogger(__name__)



class Whitebox(Node):
    def __init__(self, name, bridge_oper="br_oper0", **config):
        config.update(ports=None)
        config.update(volumes=None)
        config.update(cap_add=["ALL"])
        super(Whitebox, self).__init__(name=name, type=NodeType.SWITCH, image="vsdn/whitebox", **config)
        self.__bridge_oper = bridge_oper

    @property
    def br_oper(self):
        return self.__bridge_oper

    @br_oper.setter
    def br_oper(self, value):
        pass

    @property
    def control_addr(self):
        return iproute.get_interface_addr(ifname="eth0", netns=self.name)

    @control_addr.setter
    def control_addr(self, value):
        pass

    def set_openflow_version(self, bridge="br_oper0", version="OpenFlow13"):
        try:
            ovsdb.change_openflow_version(netns=self.name, bridge=bridge, version=version)
        except Exception as ex:
            logger.error(ex.__cause__)

    def set_manager(self, ip=None, port="6640", type="tcp"):
        try:
            ovsdb.set_manager(ip=ip, netns=self.name, port=port, type=type)
        except Exception as ex:
            logger.error(ex.__cause__)

    def set_controller(self, ip="127.0.0.1", port="6653", bridge="br_oper0", type="tcp"):
        try:
            ovsdb.set_controller(ip=ip, bridge=bridge, netns=self.name, type=type, port=port)
        except Exception as ex:
            logger.error(ex.__cause__)

    def del_controller(self, bridge="br_oper0"):
        try:
            ovsdb.del_controller(bridge=bridge, netns=self.name)
        except Exception as ex:
            logger.error(ex.__cause__)

    def add_port(self, mac=None, ip=None, mask=None):
        port = Ethernet(mac=mac, ip=ip, mask=mask)
        super().__ports.add_port(port)

    def del_port(self, id):
        try:
            super().del_port(id=id)
        except Exception as ex:
            logger.error(ex.__cause__)

    def get_port(self, id):
        return super().get_port(id=id)

    def get_len_ports(self):
        return len(self.get_ports)

    def commit(self):
        try:
            docker.create_node(name=self.name, image=self.image, **self.config)
            ovsdb.set_bridge(bridge=self.br_oper, netns=self.name)
            logger.info("the new whitebox ({name}) node was created".format(name=self.name))
        except Exception  as ex:
            logger.error(ex.with_traceback())

    def destroy(self):
        try:
            docker.delete_node(name=self.name)
            logger.info("the whitebox ({name}) node was deleted".format(name=self.name))
        except Exception as ex:
            logger.error(ex.__cause__)


if __name__ == '__main__':
    print("creating node")
    switch = Whitebox(name="sw1")
    switch.commit()
    # print(switch.control_addr)
