import ipaddress
import uuid
from enum import Enum

import docker
import pyroute2

from functions import ApiLink, ApiInterface

_client_docker = docker.from_env()
_client_iproute = pyroute2.IPRoute()


def CheckNotNull(value, msg):
    if value is None:
        raise TypeError(msg)
    else:
        return value

class TypeLink(Enum):
    Host = "host-link"
    Direct = "direct-link"


class Link(object):
    def __init__(self, type, node_source = None, node_target = None):
        self.node_source = node_source
        self.node_target = node_target
        self.type = type

    @property
    def node_source(self):
        return self.__label_source

    @node_source.setter
    def node_source(self, value):
        self.__label_source = CheckNotNull(value = value, msg = "the label of source node cannot be null")

    @property
    def node_target(self):
        return self.__label_target

    @node_target.setter
    def node_target(self, value):
        self.__label_target = CheckNotNull(value = value, msg = "the label of target node cannot be null")


    @property
    def port_source(self):
        return self.node_source.label +"-" + self.node_target.label

    @port_source.setter
    def port_source(self, value):
        pass

    @property
    def port_target(self):
        return self.node_target.label+"-"+self.node_source.label

    @port_target.setter
    def port_target(self, value):
        pass

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
        self.__type =  CheckNotNull(value = value, msg ="type of link cannot be null")


class DirectLinkOvsVeth(Link):
    def __init__(self, node_source = None, node_target = None):
        super().__init__(type = "direct-link-ovs-veth", node_source = node_source, node_target = node_target)

    def create(self):
        pass

    def delete(self):
        pass


class HostLinkOvsVeth(Link):
    def __init__(self, node_source = None, node_target = None):
        super().__init__(type = "host-link-ovs-veth", node_source = node_source, node_target = node_target)

    def create(self):
        pass

    def delete(self):
        pass

class ApiLink(object):
    @staticmethod
    def create_veth_link(port_source, port_target):


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
