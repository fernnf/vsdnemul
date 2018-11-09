import urllib3
import json
import logging

from vsdnemul.node import Node, NodeType
from vsdnemul.lib.log import get_logger
from vsdnemul.lib import dockerlib as docker

logger = logging.getLogger(__name__)

PROTOCOL_SUPPORTED = ["tcp"]

def _checkUrl(url):

    parts = url.split(":")

    if len(parts) != 3:
        raise Exception("url is not valid")

    if parts[1] not in PROTOCOL_SUPPORTED:
        raise Exception("Protocol not supported")

    try:
        int(parts[2])
    except Exception as ex:
        raise Exception("{p} is not a valid port".format(p=parts[2]))

    return url


def _makeReqConnect(addr, data, path, cmd):

    url = "http://{addr}:8080/{path}".format(addr=addr,path=path)
    conn = urllib3.PoolManager()
    headers = urllib3.util.make_headers(basic_auth="admin:", )
    headers.update({'content-type': 'application/json'})

    p = {"id": "fvctl", "method": cmd, "jsonrpc": "2.0"}
    p["params"] = data

    return conn.request("POST", url=url, body=json.dumps(p), headers=headers)

def _makeReqNetwork(ctl_url, net_addr, net_mask):
    data = {}

    data["controllerUrls"] = ctl_url
    data["networkAddress"] = net_addr
    data["mask"] = int(net_mask)

    return data

def _makeReqSwitch(tenant, dpids, dpid):
    data = {}

    data["tenantId"] = tenant
    data["dpids"] = dpids
    data["dpid"] = dpid

    return data


def _makeReqPort(tenant, dpid, port):
    data = {}

    data["tenantId"] = tenant
    data["dpid"] = dpid
    data["port"] = port

    return data


def _makeReqLink(tenant, src_vdpid, src_vport, dst_vdpid, dst_vport, algo, bkp):
    data = {}

    data["tenantId"] = tenant
    data["srcDpid"] =  src_vdpid
    data["srcPort"] = src_vport
    data["dstDpid"] = dst_vdpid
    data["dstPort"] = dst_vport
    data["algorithm"] = algo
    data["backup_num"] = bkp

    return data


def _makeReqHost(tenant, vdpid, vport, mac):
    data = {}

    data["tenantId"] = tenant
    data["vdpid"] = vdpid
    data["vport"] = vport
    data["mac"] =  mac

    return data


def _makeReqStart(tenant):
    data = {}

    data["tenantId"] = tenant

    return data


class OpenVirtex(Node):

    __image__ = "vsdn/openvirtex"
    __cap_add__ = ["ALL"]
    __volumes__ = {"/sys/fs/cgroup": {"bind": "/sys/fs/cgroup", "mode": "ro"}}
    __type__ = NodeType.HYPERVISOR

    logger = get_logger(__name__)

    def __init__(self, name, image):
        super().__init__(name, image, type=self.__type__)
        self.config.update(cap_add=self.__cap_add__)
        self.config.update(volumes=self.__volumes__)

    def getManagerAddr(self):
        return "tcp:{ip}:6633".format(ip=self.getControlIp())

    def createNetwork(self, ctl_url,net_addr, net_mask):
        try:
            url = _checkUrl(ctl_url)
            addr = net_addr
            mask = int(net_mask)

            req = _makeReqNetwork(url, addr, mask)
            ret = _makeReqConnect(self.getControlIp(), req, "tenant", "createNetwork")

            return json.loads(ret.data)["result"]

        except Exception as ex:
            logger.error(ex)


    def createSwitch(self,tenant, dpids, dpid):
        try:
            tnt = int(tenant)
            dps = [int(dp.replace(":", ""), 16) for dp in dpids.split(",")]
            dp = int(dpid.replace(":", ""), 16)

            req = _makeReqSwitch(tnt, dps, dp)
            ret = _makeReqConnect(self.getControlIp(), req, "tenant", "createSwitch")

            return json.loads(ret.data)["result"]

        except Exception as ex:
            logger.error(ex)

    def createPort(self,tenant, dpid, port):
        try:
            tnt = int(tenant)
            dp = int(dpid.replace(":", ""), 16)
            pt = int(port)

            req = _makeReqPort(tnt, dp, pt)
            ret = _makeReqConnect(self.getControlIp(), req, "tenant", "createPort")

            return json.loads(ret.data)["result"]

        except Exception as ex:
            logger.error(ex)

    def connectLink(self,tenant, src_vdpid, src_vport, dst_vdpid, dst_vport, algo="spf", bkp="1"):

        try:
            tnt = int(tenant)
            s_dp = int(src_vdpid.split(":"), 16)
            s_pt = int(src_vport)
            d_dp = int(dst_vdpid.split(":"), 16)
            d_pt = int(dst_vport)
            al = algo
            bk = int(bkp)

            req = _makeReqLink(tnt,s_dp,s_pt,d_dp,d_pt,al,bk)
            ret = _makeReqConnect(self.getControlIp(), req, "tenant", "connectLink")

            return json.loads(ret.data)["result"]

        except Exception as ex:
            logger.error(ex)


    def connectHost(self,tenant, vdpid, vport, mac):
        try:
            tnt = int(tenant)
            vdp = int(vdpid.replace(":", ""), 16)
            vpt = int(vport)
            mc = mac

            req = _makeReqHost(tnt, vdp, vpt, mc)
            ret = _makeReqConnect(self.getControlIp(), req, "tenant", "connectHost")

            return json.loads(ret.data)["result"]

        except Exception as ex:
            logger.error(ex)

    def startNetwork(self, tenant):
        try:
            tnt = int(tenant)

            req = _makeReqStart(tnt)
            ret = _makeReqConnect(self.getControlIp(), req, "tenant", "startSwitch")

            return json.loads(ret.data)["result"]

        except Exception as ex:
            logger.error(ex)

    def setInterface(self, ifname, encap):
        pass

    def delInterface(self, id):
        pass

    def _Commit(self):
        try:
            docker.create_node(name=self.getName(), image=self.getImage(), **self.config)
            logger.info("the new hypervisor ({name}) node was created".format(name=self.getName()))
            logger.info("waiting for flowvisor process")
            status = False
            while not False:


        pass

    def _Destroy(self):
        pass