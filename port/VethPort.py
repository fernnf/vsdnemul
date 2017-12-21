from api.port.portapi import Port
from api.iproute.iprouteapi import IpRouteApi
from api.log.logapi import get_logger


class VethPort(Port):

    logger = get_logger("VethPort")

    def __init__(self, name, peer=None):
        super().__init__(name = name, type = "VETH")
        self.__peer = peer

    @property
    def peer(self):
        return self.__peer

    def create_port(self):

        try:
            if self.__peer is None:
                IpRouteApi.create_pair(ifname = self.name)
            else:
                IpRouteApi.create_pair(ifname = self.name, peer = self.__peer)
        except Exception as ex:
            self.logger.error(ex.args[0])

    def delete_port(self, netns=None):
        try:
            if netns is None:
                IpRouteApi.delete_port(self.name)
            else:
                IpRouteApi.delete_port(self.name, netns = netns)
        except Exception as ex:
            self.logger.error(ex.args[0])


