import logging

import requests

from vsdnemul.lib import dockerlib as docker
from vsdnemul.lib import iproutelib as iproute
from vsdnemul.node import Node, NodeType

logger = logging.getLogger(__name__)

"""Begin self API for special commands"""


def _GetManagerAddr(node):
    def get_ip():
        return iproute.get_interface_addr(ifname="eth0", netns=node)

    return "tcp:{ip}:6640".format(ip=get_ip())


def _GetIpController(node):
    return iproute.get_interface_addr(ifname="eth0", netns=node)


def _DisableApp(ctl_ip, name_app):
    url = "http://{addr}:8181/onos/v1/applications/{app}/deactive".format(addr=ctl_ip, app=name_app)
    with requests.Session() as r:
        a = requests.adapters.HTTPAdapter(max_retries=10)
        r.mount("http://", a)
        resp = r.delete(url=url, auth=("karaf", "karaf"))
        if not resp.ok:
            raise RuntimeError("cannot disable application")


def _EnableApp(ctl_ip, name_app):
    URL = "http://{addr}:8181/onos/v1/applications/{app}/active".format(addr=ctl_ip, app=name_app)

    with requests.Session() as r:
        a = requests.adapters.HTTPAdapter(max_retries=10)
        r.mount("http://", a)
        resp = r.post(url=URL, auth=("karaf", "karaf"))
        if not resp.ok:
            raise RuntimeError("cannot enable application")


"""End self API"""


class Onos(Node):
    __image__ = "vsdn/onos"
    __ports__ = {'6653/tcp': None, '6640/tcp': None, '8181/tcp': None, '8101/tcp': None, '9876/tcp': None}
    __volumes__ = {"/sys/fs/cgroup": {"bind": "/sys/fs/cgroup", "mode": "ro"}}
    __cap_add__ = ["SYS_ADMIN", "NET_ADMIN"]
    __type__ = NodeType.CONTROLLER

    def __init__(self, name):
        super(Onos, self).__init__(name=name, image=self.__image__, type=self.__type__)
        self.config.update(ports=self.__ports__)
        self.config.update(cap_add=self.__cap_add__)
        self.config.update(volumes=self.__volumes__)


    def getManagerAddr(self):
        return _GetManagerAddr(node=self.getName())

    def getIpController(self):
        return _GetIpController(node=self.getName())

    def setStartApp(self, app_name):
        try:
            _EnableApp(self.getIpController(), name_app=app_name)
        except Exception as ex:
            logger.error(ex.args[0])

    def setStopApp(self, app_name):
        try:
            _DisableApp(self.getIpController(), name_app=app_name)
        except Exception as ex:
            logger.error(ex.args[0])

    def setInterface(self, ifname, encap):
        pass

    def delInterface(self, id):
        pass

    def _Commit(self):
        try:
            docker.create_node(name=self.getName(), image=self.getImage(), **self.config)
            logger.info("the new controller onos ({name}) node was created".format(name=self.getName()))
            logger.info(
                "the controller web interface can be accessed by address http://{ip}:8181/onos/ui/index.html".format(
                    ip=self.getIpController()))
        except Exception as ex:
            logger.error(ex.args[0])

    def _Destroy(self):
        try:
            docker.delete_node(name=self.getName())
            logger.info("the controller onos ({name}) node was deleted".format(name=self.getName()))
        except Exception as ex:
            logger.error(ex.args[0])
