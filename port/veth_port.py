from api.port.portapi import Port, PortType
from api.iproute.iprouteapi import IpRouteApi
from api.log.logapi import get_logger

logger = get_logger("EethPort")


class SwitchEthPort(Port):

    def __init__(self, idx, mtu = "1500"):
        super().__init__(idx = idx, name = "eth{i}".format(i=idx), type = PortType.ETHERNET)



