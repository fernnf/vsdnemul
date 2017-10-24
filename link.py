import logging
import ipaddress
import uuid

from functions import ApiLink, ApiInterface
from enum import Enum


class TypeLink(Enum):
    Host = "host-link"
    Direct = "direct-link"


class Link(object):
    def __init__(self, source = None, target = None, type = TypeLink):
        self.id = uuid.uuid4()
        self.source = source
        self.node_target = target
        self.type = type
        self.log = logging.getLogger("link.Link")

    def __str__(self):
        str = {
            "id": self.id,
            "node_source": self.node_source,
            "node_target": self.node_target,
            "intf_source": self.intf_source,
            "intf_target": self.intf_target,
            "type": self.type
        }
        return str

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, value):
        if self.__id is None:
            if isinstance(value, uuid.uuid4()):
                self.__id = value
            else:
                raise AttributeError("the attribute id must be type UUID 4")
    @property
    def node_source(self):
        return self.__source

    @node_source.setter
    def node_source(self, value):
        if None:
            self.log.error("source must be a node object")
        self.__source = value

    @property
    def node_target(self):
        return self.__target

    @node_target.setter
    def node_target(self, value):
        if None:
            self.log.error("target must be a node object")
        self.__target = value

    @property
    def intf_source(self):
        return self.node_source + "-" + self.node_target

    @intf_source.setter
    def intf_source(self, value):
        pass

    @property
    def intf_target(self):
        return self.node_target + "-" + self.node_source

    @intf_target.setter
    def intf_target(self, value):
        pass

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
        if value is None:
            raise AttributeError("Type cannot be null")
        self.__type = value


class LinkSwitch(Link):
    def __init__(self, source, target):
        super().__init__(source, target, TypeLink.Switch.value)

    def create(self):
        ApiLink.linkCreateVethPeerInterfaces(ifname_src = self.intf_source, ifname_dst = self.intf_target)
        ApiLink.linkVethPairingNodes(self.node_source, self.node_target, self.intf_source, self.intf_target)
        ApiInterface.intfAddSystemInterfaceToBridge(self.node_source, self.intf_source)
        ApiInterface.intfAddSystemInterfaceToBridge(self.node_target, self.intf_target)

    def delete(self):
        ApiLink.linkVethUnpairingNodes(self.node_source, self.node_target, self.intf_source, self.intf_target)
        ApiInterface.intfRemoveInterfaceFromBridge(self.node_source, self.intf_source)
        ApiInterface.intfRemoveInterfaceFromBridge(self.node_target, self.intf_target)

class LinkHost(Link):
    def __init__(self, host, target, ip, mask, gateway):
        super().__init__(host, target, TypeLink.Host.value)
        self.ip = ip
        self.mask = mask
        self.gateway = gateway

    @property
    def ip(self):
        return self.__ip

    @ip.setter
    def ip(self, value):
        try:
            ipaddress.ip_address(value)
            self.__ip = value
        except Exception as ex:
            raise ValueError("The atributed ip is not valid")

    @property
    def mask(self):
        return self.__mask

    @mask.setter
    def mask(self, value):
        try:
            ipaddress.ip_address(value)
            self.__mask = value
        except Exception as ex:
            raise ValueError("The atributed mask is not valid")

    @property
    def gateway(self):
        return self.__gateway

    @gateway.setter
    def gateway(self, value):
        try:
            ipaddress.ip_address(value)
            self.__gateway = value
        except Exception as ex:
            raise ValueError("The atributed gateway is not valid")

    def create(self):
        ApiLink.linkCreateVethPeerInterfaces(ifname_src = self.intf_source, ifname_dst = self.intf_target)
        ApiLink.linkVethPairingNodes(self.node_source, self.node_target, self.intf_source, self.intf_target)
        ApiInterface.intfConfgAddressInterface(self.node_source, self.ip, self.mask)
        ApiInterface.intfAddSystemInterfaceToBridge(self.node_target, self.intf_target)

    def delete(self):
        ApiLink.linkVethUnpairingNodes(self.node_source, self.node_target, self.intf_source, self.intf_target)
        ApiInterface.intfRemoveInterfaceFromBridge(self.node_source, self.intf_source)
        ApiInterface.intfRemoveInterfaceFromBridge(self.node_target, self.intf_target)

class LinkCommand(object):
    @staticmethod
    def createHostLink(link = LinkHost):
        try:
           link.create()
        except Exception as ex:
            raise ValueError("LinkCommandError:" + ex.args[0])

    def deleteHostLink

    @staticmethod
    def createSwitchLink(link = LinkSwitch):
        try:
            link.create()
        except Exception as ex:
            print("LinkCommandError:" + ex.args[0])

    @staticmethod
    def delete(link):
        def _sw_delete():
            ApiLink.linkVethUnpairingNodes(link.node_source, link.node_target, link.intf_source, link.intf_target)
            ApiInterface.intfRemoveInterfaceFromBridge(link.node_source, link.intf_source)
            ApiInterface.intfRemoveInterfaceFromBridge(link.node_target, link.intf_target)

        def _ht_delete():
            ApiLink.linkVethUnpairingNodes(link.node_source, link.node_target, link.intf_source, link.intf_target)
            ApiInterface.intfRemoveInterfaceFromBridge(link.node_target, link.intf_target)

        try:
            if isinstance(link, LinkSwitch):
                _sw_delete()
            elif isinstance(link, LinkHost):
                _ht_delete()
            else:
                raise ValueError("the link object is unknown")
        except Exception as ex:
            print(ex.args[0])
