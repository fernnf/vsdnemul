import logging

import requests

from vsdnemul.lib import dockerlib as docker
from vsdnemul.lib import iproutelib as iproute
from vsdnemul.node import Node, NodeType

logger = logging.getLogger(__name__)

"""Begin self API for special commands"""


def _get_mngt_addr(node):
    def get_ip():
        return iproute.get_interface_addr(ifname="eth0", netns=node)

    return "tcp:{ip}:6640".format(ip=get_ip())


def _get_ip_controller(node):
    def get_ip():
        return iproute.get_interface_addr(ifname="eth0", netns=node)

    return get_ip()


def _disable_app(ctl_ip, name_app):
    url = "http://{addr}:8181/onos/v1/applications/{app}/deactive".format(addr=ctl_ip, app=name_app)
    with requests.Session() as r:
        a = requests.adapters.HTTPAdapter(max_retries=10)
        r.mount("http://", a)
        resp = r.delete(url=url, auth=("karaf", "karaf"))
        if not resp.ok:
            raise RuntimeError("cannot disable application")


def _enable_app(ctl_ip, name_app):
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

    def __init__(self, name, **config):
        config.update(ports=self.__ports__)
        config.update(volumes=self.__volumes__)
        config.update(cap_add=self.__cap_add__)
        super(Onos, self).__init__(name=name, image=self.__image__, type=self.__type__, **config)

    @property
    def control_addr(self):
        try:
            return _get_mngt_addr(self.name)
        except Exception as ex:
            logger.error(ex.args[0])
            return None

    @control_addr.setter
    def control_addr(self, value):
        pass

    @property
    def ip_controller(self):
        return _get_ip_controller(self.name)

    @ip_controller.setter
    def ip_controller(self, value):
        pass

    def start_app(self, app_name):

        try:
            _enable_app(ctl_ip=self.ip_controller, name_app=app_name)
        except Exception as ex:
            logger.error(str(ex.args[0]))

    def stop_app(self, app_name):

        try:
            _disable_app(ctl_ip=self.ip_controller, name_app=app_name)
        except Exception as ex:
            logger.error(str(ex.args[0]))

    def _Commit(self):
        try:
            docker.create_node(name=self.name, image=self.image, **self.config)
            logger.info("the new controller onos ({name}) node was created".format(name=self.name))
            logger.info(
                "the controller web interface can be accessed by address http://{ip}:8181/onos/ui/index.html".format(
                    ip=self.ip_controller))
        except Exception as ex:
            logger.error(ex.args[0])

    def _Destroy(self):
        try:
            docker.delete_node(name=self.name)
            logger.info("the controller onos  ({name}) node was deleted".format(name=self.name))
        except Exception as ex:
            logger.error(ex.args[0])
