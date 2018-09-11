import logging
from uuid import uuid4

from vsdnemul.lib import iproutelib as iproute
from vsdnemul.link import Link, LinkEncap, LinkType

MTU_DEFAULT = 9000

logger = logging.getLogger(__name__)


def _GetVethName():
    return "veth{id}".format(id=str(uuid4())[:6])


def _CreateVeth(mtu):
    source = _GetVethName()
    target = _GetVethName()
    if iproute.create_pair(ifname=source, peer=target, mtu=mtu):
        return source, target
    return None


def _CreateBridge(name, mtu, slaves:list=None):
    return iproute.create_bridge(ifname=name, slaves=slaves, mtu=mtu)


def _DeleteBridge(name):
    return iproute.delete_port(ifname=name)


def _CreateLink(bridge, mtu):
    source, br_source = _CreateVeth(mtu)
    target, br_target = _CreateVeth(mtu)

    _CreateBridge(name=bridge, mtu=mtu, slaves=[br_source, br_target])

    return source, target


class Bridge(Link):
    __encap__ = LinkEncap.ETHERNET

    def __init__(self, name, node_source, node_target, type: LinkType, mtu=MTU_DEFAULT):
        super(Bridge, self).__init__(name=name, node_source=node_source, node_target=node_target, type=type, encap=self.__encap__)
        self.__mtu = mtu

    def getMtu(self):
        return self.__mtu

    def _Commit(self):
        try:
            source, target = _CreateLink(bridge=self.getIfName(), mtu=self.getMtu())

            node_source = self.getSource()
            node_target = self.getTarget()

            src_id = node_source.setInterface(ifname=source, encap=self.__encap__)
            tgt_id = node_target.setInterface(ifname=target, encap=self.__encap__)

            self.setPortSource(src_id)
            self.setPortTarget(tgt_id)

            logger.info(
            "The new link has created between ({src}-{src_id} <--> {tgt_id}-{tgt}))".format(src=node_source.getName(),
                                                                                        src_id=src_id,
                                                                                        tgt=node_target.getName(),
                                                                                        tgt_id=tgt_id))

        except Exception as ex:
            logger.error(ex.args[0])

    def _Destroy(self):
        try:
            node_source = self.getSource()
            node_target = self.getTarget()

            node_source.delInterface(self.getPortSource())
            node_target.delInterface(self.getPortTarget())

            _DeleteBridge(self.getIfName())

            logger.info(
                "The link has deleted between ({src}-{src_id} <--> {tgt_id}-{tgt}))".format(src=node_source.getName(),
                                                                                            src_id=self.getPortSource(),
                                                                                            tgt=node_target.getName(),
                                                                                            tgt_id=self.getPortTarget()))
        except Exception as ex:
            logger.error(ex.args[0])


