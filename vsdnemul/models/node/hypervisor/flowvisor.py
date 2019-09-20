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

import urllib3

from vsdnemul.lib import dockerlib as docker
from vsdnemul.node import Node, NodeType

urllib3.disable_warnings()

logger = logging.getLogger(__name__)


def _checkStatus(addr, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((addr, port))
    if result == 0:
        return True
    else:
        return False


def _makeMatch(match):
    matchItem = match.split(",")

    m = {}

    for item in matchItem:
        it = item.split("=")
        if it[0].__eq__("in_port"):
            m[it[0]] = int(it[1])

        elif it[0].__eq__("dl_vlan"):
            m[it[0]] = int(it[1])

        elif it[0].__eq__("dl_src"):
            m[it[0]] = str(it[1])

        elif it[0].__eq__("dl_dst"):
            m[it[0]] = str(it[1])

        elif it[0].__eq__("dl_type"):
            m[it[0]] = int(it[1])

        elif it[0].__eq__("nw_tos"):
            m[it[0]] = int(it[1])

        elif it[0].__eq__("nw_proto"):
            m[it[0]] = int(it[1])

        elif it[0].__eq__("nw_src"):
            m[it[0]] = str(it[1])

        elif it[0].__eq__("nw_dst"):
            m[it[0]] = str(it[1])

        elif it[0].__eq__("tp_src"):
            m[it[0]] = int(it[1])

        elif it[0].__eq__("tp_dst"):
            m[it[0]] = int(it[1])

        elif it[0].__eq__("dl_vlan_pcp"):
            m[it[0]] = str(it[1])

        else:
            raise Exception("Action not found")

    return m


def _makeReqFlowSpace(name, dpid, priority, match, slice, slice_perm):
    req = {}
    req["name"] = name
    req["dpid"] = dpid
    req["priority"] = priority

    req["match"] = match

    acts = []
    act = {"slice-name": slice, "permission": slice_perm}

    acts.append(act)

    req["slice-action"] = acts

    result = []
    result.append(req)

    return result


def _makeReqSlice(name, controller_url):
    req = {}
    req["slice-name"] = name
    req["controller-url"] = controller_url
    req["admin-contact"] = "vsdnemul@localhost"
    req["password"] = "flowvisor"

    return req


def _makeConnect(addr, data, cmd):
    url = "https://{addr}:8081".format(addr=addr)

    conn = urllib3.PoolManager()

    headers = urllib3.util.make_headers(basic_auth="fvadmin:flowvisor", )
    headers.update({'content-type': 'application/json'})

    p = {"id": "fvctl", "method": cmd, "jsonrpc": "2.0", "params": data}

    return conn.request("POST", url=url, body=json.dumps(p), headers=headers, verify=False)


class FlowVisor(Node):
    __image__ = "vsdn/flowvisor"
    __cap_add__ = ["ALL"]
    __volumes__ = {"/sys/fs/cgroup": {"bind": "/sys/fs/cgroup", "mode": "ro"}}
    __type__ = NodeType.HYPERVISOR

    def __init__(self, name):
        super(FlowVisor, self).__init__(name=name, image=self.__image__, type=self.__type__)
        self.config.update(cap_add=self.__cap_add__)
        self.config.update(volumes=self.__volumes__)

    def getManagerAddr(self):
        return "tcp:{ip}:6633".format(ip=self.getControlIp())

    def setFlowSpace(self, name, dpid, prio, slice, match, slice_perm=7):
        try:
            req = _makeReqFlowSpace(name=name, dpid=dpid, match=_makeMatch(match), priority=prio, slice=slice,
                                    slice_perm=slice_perm)
            logger.info("Creating FlowSpace")
            ret = _makeConnect(addr=self.getControlIp(), data=req, cmd="add-flowspace")
            logger.info(str(ret.read()))
            return ret
        except Exception as ex:
            logger.error(str(ex))

    def setSlice(self, name, ctl_url):
        try:
            req = _makeReqSlice(name=name, controller_url=ctl_url)
            logger.info("Creating Slice ({name})".format(name=name))
            logger.info("{}".format(req))
            ret = _makeConnect(addr=self.getControlIp(), data=req, cmd="add-slice")
            logger.info(str(ret.read()))
            return ret
        except Exception as ex:
            logger.error(str(ex))

    def run_command(self, cmd):
        try:
            return docker.run_cmd(name=self.getName(), cmd=cmd)
        except Exception as ex:
            logger.error(str(ex))

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
            while not status:
                status = _checkStatus(addr=self.getControlIp(), port=8081)

        except Exception as ex:
            logger.error(ex)

    def _Destroy(self):
        try:
            docker.delete_node(name=self.getName())
            logger.info("the hypervisor ({name}) node was deleted".format(name=self.getName()))

        except Exception as ex:
            logger.error(ex)
