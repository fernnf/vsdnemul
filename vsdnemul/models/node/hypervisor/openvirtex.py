#  Copyright @2018
#
#  GERCOM - Federal University of Pará - Brazil
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import json
import logging
import socket
import time

import urllib3

from vsdnemul.lib import dockerlib as docker
from vsdnemul.lib.log import get_logger
from vsdnemul.node import Node, NodeType

logger = logging.getLogger(__name__)

PROTOCOL_SUPPORTED = ["tcp"]


def _checkStatus(addr, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((addr, port))
    if result == 0:
        return True
    else:
        return False


def _checkUrl(url):
    parts = url.split(":")

    if len(parts) != 3:
        raise Exception("url is not valid")

    if not parts[0] in PROTOCOL_SUPPORTED:
        raise Exception("Protocol not supported")
    try:
        int(parts[2])
    except Exception as ex:
        raise Exception("{p} is not a valid port".format(p=parts[2]))

    return url


def _makeReqConnect(addr, data, path, cmd):
    url = "http://{addr}:8080/{path}".format(addr=addr, path=path)
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
    data["srcDpid"] = src_vdpid
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
    data["mac"] = mac

    return data


def _makeReqStart(tenant):
    data = {}

    data["tenantId"] = tenant

    return data


def _makeReqSwitchStart(tenant, vdpid):
    data = {}

    data["tenantId"] = tenant
    data["vdpid"] = vdpid

    return data


def _makeReqPortStart(tenant, vdpid, vport):
    data = {}

    data["tenantId"] = tenant
    data["vdpid"] = vdpid
    data["vport"] = vport

    return data


class OpenVirtex(Node):
    __image__ = "vsdn/openvirtex"
    __cap_add__ = ["ALL"]
    __volumes__ = {"/sys/fs/cgroup": {"bind": "/sys/fs/cgroup", "mode": "ro"}}
    __type__ = NodeType.HYPERVISOR

    logger = get_logger(__name__)

    def __init__(self, name):
        super().__init__(name, image=self.__image__, type=self.__type__)
        self.config.update(cap_add=self.__cap_add__)
        self.config.update(volumes=self.__volumes__)

    def getManagerAddr(self):
        return "tcp:{ip}:6633".format(ip=self.getControlIp())

    def createNetwork(self, ctl_url, net_addr, net_mask):
        try:
            time.sleep(2)
            url = [_checkUrl(ctl_url)]
            addr = net_addr
            mask = int(net_mask)

            req = _makeReqNetwork(url, addr, mask)
            ret = _makeReqConnect(self.getControlIp(), req, "tenant", "createNetwork")
            tnt = json.loads(ret.data)["result"].get("tenantId")
            logger.info("new virtual network created tenant={t}".format(t=tnt))
            return tnt

        except Exception as ex:
            logger.error(ex)

    def createSwitch(self, tenant, dpids):
        try:
            time.sleep(1)
            tnt = int(tenant)
            dps = [int(dp.replace(":", ""), 16) for dp in dpids.split(",")]
            dp = 0

            req = _makeReqSwitch(tnt, dps, dp)
            ret = _makeReqConnect(self.getControlIp(), req, "tenant", "createSwitch")
            switchId = json.loads(ret.data)["result"].get("vdpid")

            sw_name = '00:' + ':'.join([("%x" % switchId)[i:i + 2] for i in range(0, len(("%x" % switchId)), 2)])

            logger.info("new virtual switch created tenant={t} switch={s}".format(t=tnt, s=sw_name))
            return sw_name

        except Exception as ex:
            logger.error(ex)

    def createPort(self, tenant, dpid, port):
        try:
            time.sleep(1)
            tnt = int(tenant)
            dp = int(dpid.replace(":", ""), 16)
            pt = int(port)

            req = _makeReqPort(tnt, dp, pt)
            ret = _makeReqConnect(self.getControlIp(), req, "tenant", "createPort")
            vport = json.loads(ret.data)["result"].get("vport")

            logger.info("new virtual port created tenant={t} switch={s} port={p}".format(t=tnt, s=dpid, p=vport))

            return str(vport)

        except Exception as ex:
            logger.error(ex)

    def connectLink(self, tenant, src_vdpid, src_vport, dst_vdpid, dst_vport, algo="spf", bkp="1"):

        try:
            time.sleep(1)
            tnt = int(tenant)
            s_dp = int(src_vdpid.replace(":", ""), 16)
            s_pt = int(src_vport)
            d_dp = int(dst_vdpid.replace(":", ""), 16)
            d_pt = int(dst_vport)
            al = algo
            bk = int(bkp)

            req = _makeReqLink(tnt, s_dp, s_pt, d_dp, d_pt, al, bk)
            ret = _makeReqConnect(self.getControlIp(), req, "tenant", "connectLink")
            link = json.loads(ret.data)["result"].get("linkId")

            logger.info(
                "new virtual link created tenant={t} switch={s1}/{p1}<->{s2}/{p2} vlink={v}".format(t=tnt, s1=src_vdpid,
                                                                                                    p1=src_vport,
                                                                                                    s2=dst_vdpid,
                                                                                                    p2=dst_vport,
                                                                                                    v=link))
            return link

        except Exception as ex:
            logger.error(ex)

    def connectHost(self, tenant, vdpid, vport, mac):
        try:
            time.sleep(1)
            tnt = int(tenant)
            vdp = int(vdpid.replace(":", ""), 16)
            vpt = int(vport)
            mc = mac

            req = _makeReqHost(tnt, vdp, vpt, mc)
            ret = _makeReqConnect(self.getControlIp(), req, "tenant", "connectHost")
            logger.info(
                "new virtual host created tenant={t} switch={s} port={p} mac={m}".format(t=tnt, s=vdpid, p=vport,
                                                                                         m=mac))
            return json.loads(ret.data)["result"]

        except Exception as ex:
            logger.error(ex)

    def startNetwork(self, tenant):
        try:
            time.sleep(1)
            tnt = int(tenant)

            req = _makeReqStart(tnt)
            ret = _makeReqConnect(self.getControlIp(), req, "tenant", "startNetwork")
            start = json.loads(ret.data)["result"].get("isBooted")
            logger.info(
                "new virtual host created tenant={t} start={s}".format(t=tenant, s=start))
            return bool(start)

        except Exception as ex:
            logger.error(ex)
            return False

    def startSwitch(self, tenant, vdpid):

        try:
            time.sleep(1)

            tnt = int(tenant)
            vdp = int(vdpid.replace(":", ""), 16)

            req = _makeReqSwitchStart(tnt, vdp)
            ret = _makeReqConnect(self.getControlIp(), req, "tenant", "startSwitch")

            error = json.loads(ret.data).get("error")

            if error is None:
                return True
            else:
                logger.error(str(error))
                return False

        except Exception as ex:
            logger.error(ex)
            return False

    def startPort(self, tenant, vdpid, vport):
        try:
            time.sleep(1)

            tnt = int(tenant)
            vdp = int(vdpid.replace(":", ""), 16)
            vp = int(vport)

            req =  _makeReqPortStart(tnt,vdp,vp)
            ret = _makeReqConnect(self.getControlIp(), req, "tenant", "startPort")

            error = json.loads(ret.data).get("error")

            if error is None:
                return True
            else:
                logger.error(str(error))
                return False
        except Exception as ex:
            logger.error(ex)
            return False

    def checkSwitchConnected(self):
        def connect():
            req = {}
            ret = _makeReqConnect(self.getControlIp(), req, "status", "getPhysicalTopology")
            rep = json.loads(ret.data)["result"].get("switches")
            logger.info("swichted connected ({s})".format(s=len(rep)))
            if len(rep) > 0:
                return True
            else:
                return False

        try:
            return connect()
        except Exception as ex:
            logger.error("not connected..: {xe}".format(xe=ex))
            return False

    def setInterface(self, ifname, encap):
        pass

    def delInterface(self, id):
        pass

    def _Commit(self):
        try:
            docker.create_node(name=self.getName(), image=self.getImage(), **self.config)
            logger.info("the new hypervisor ({name}) node was created".format(name=self.getName()))
            logger.info("waiting for openvirtex process")
            status = False
            while not status:
                status = _checkStatus(self.getControlIp(), 8080)

        except Exception as ex:
            logger.error(ex)

    def _Destroy(self):
        try:
            docker.delete_node(name=self.getName())
            logger.info("the hypervisor ({name}) node was deleted".format(name=self.getName()))

        except Exception as ex:
            logger.error(ex)
