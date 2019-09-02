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

import logging
import socket

from vsdnemul.lib import dockerlib as docker
from vsdnemul.node import Node, NodeType

logger = logging.getLogger(__name__)


def _check_status(addr, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((addr, port))
    if result == 0:
        return True
    else:
        return False


class VSDNOrches(Node):
    __image__ = "vsdn/vsdnorches"
    __cap_add__ = ["ALL"]
    __volumes__ = {"/sys/fs/cgroup": {"bind": "/sys/fs/cgroup", "mode": "ro"}}
    __environment__ = ["container=docker"]
    __ports__ = {"8080/tcp": "8080"}
    __type__ = NodeType.HYPERVISOR

    def __init__(self, name):
        super().__init__(name=name, image=self.__image__, type=self.__type__)
        self.config.update(cap_add=self.__cap_add__)
        self.config.update(volumes=self.__volumes__)
        self.config.update(ports=self.__ports__)
        self.config.update(environment=self.__environment__)

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
            logger.info("waiting for vsdnorches process")
            status = False
            while not status:
                status = _check_status(self.getControlIp(), 8080)

        except Exception as ex:
            logger.error(str(ex))

    def _Destroy(self):
        try:
            docker.delete_node(name=self.getName())
            logger.info("the hypervisor ({name}) node was deleted".format(name=self.getName()))
        except Exception as ex:
            logger.error(str(ex))
