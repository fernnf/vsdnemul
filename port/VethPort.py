from api.port.portapi import Port
from api.iproute.iprouteapi import IpRouteApi
from api.log.logapi import get_logger


class VethPort(Port):

    logger = get_logger("VethPort")

    def __init__(self, ifname, peer=None):
        super().__init__(ifname = ifname, type = "VETH")
        self.__peer = peer

    @property
    def peer(self):
        return self.__peer

    def create_port(self):

        try:
            if self.__peer is None:
                IpRouteApi.create_pair(ifname = self.ifname)
            else:
                IpRouteApi.create_pair(ifname = self.ifname, peer = self.__peer)
        except Exception as ex:
            self.logger.error(ex.args[0])

    def delete_port(self, netns=None):
        try:
            if netns is None:
                IpRouteApi.delete_port(self.ifname)
            else:
                IpRouteApi.delete_port(self.ifname, netns = netns)
        except Exception as ex:
            self.logger.error(ex.args[0])


