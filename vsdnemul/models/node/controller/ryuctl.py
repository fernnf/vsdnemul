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

from vsdnemul.lib import dockerlib as docker
from vsdnemul.lib import iproutelib as iproute
from vsdnemul.node import Node, NodeType

logger = logging.getLogger(__name__)


def get_ip_control(node):
    return iproute.get_interface_addr(ifname="eth0", netns=node)


class Ryuctl(Node):
    __image__ = "vsdn/ryuctl"
    __ports__ = {'6653/tcp': "6653"}
    __volumes__ = {"/sys/fs/cgroup": {"bind": "/sys/fs/cgroup", "mode": "ro"}}
    __cap_add__ = ["SYS_ADMIN", "NET_ADMIN"]
    __type__ = NodeType.CONTROLLER

    def __init__(self, name):
        super().__init__(name, image=self.__image__, type=self.__type__)
        self.config.update(ports=self.__ports__)
        self.config.update(cap_add=self.__cap_add__)
        self.config.update(volumes=self.__volumes__)

    def getControlIp(self):
        return get_ip_control(self.getName())

    def _Commit(self):
        try:
            docker.create_node(name=self.getName(), image=self.getImage(), **self.config)
            logger.info("the new controller onos ({name}) node was created".format(name=self.getName()))
            logger.info(
                "the RYU controller is enable on address tcp:{ip}:6653".format(
                    ip=self.getControlIp()))
        except Exception as ex:
            logger.error(str(ex))

    def _Destroy(self):
        try:
            docker.delete_node(name=self.getName())
            logger.info("the RYU controller ({name}) node was deleted".format(name=self.getName()))
        except Exception as ex:
            logger.error(str(ex))

    def setInterface(self, ifname, encap):
        pass

    def delInterface(self, id):
        pass
