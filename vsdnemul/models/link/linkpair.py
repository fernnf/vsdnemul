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



class LinkPair(Link):
    __encap__ = LinkEncap.ETHERNET

    def __init__(self, name, node_source, node_target, type: LinkType, mtu = MTU_DEFAULT):
        super(LinkPair, self).__init__(name, node_source, node_target, type, encap = self.__encap__)

        self.__mtu = mtu

    def getMtu(self):
        return self.__mtu

    def _Commit(self):

        try:
            source, target = _CreateVeth(mtu=self.getMtu())

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
            node_source.delInterface(self.getPortSource())

        except Exception as ex:
            logger.error(ex.args[0])

