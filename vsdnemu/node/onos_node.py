import requests

from vsdnemu.api.docker.dockerapi import DockerApi
from vsdnemu.api.log.logapi import get_logger
from vsdnemu.api.node.nodeapi import Node, NodeType
from vsdnemu.api.utils.utils import check_not_null

logger = get_logger(__name__)


def _disable_app(ctl_ip, name_app):
    check_not_null(ctl_ip, "the controller ip cannot be null")
    check_not_null(name_app, "the onos app cannot be null")

    url = "http://{addr}:8181/onos/v1/applications/{app}/deactive".format(addr = ctl_ip, app = name_app)
    with requests.Session() as r:
        a = requests.adapters.HTTPAdapter(max_retries = 10)
        r.mount("http://", a)
        resp = r.delete(url = url, auth = ("karaf", "karaf"))
        if not resp.ok:
            raise RuntimeError("cannot disable application")


def _enable_app(ctl_ip, name_app):
    URL = "http://{addr}:8181/onos/v1/applications/{app}/active".format(addr = ctl_ip, app = name_app)

    with requests.Session() as r:
        a = requests.adapters.HTTPAdapter(max_retries = 10)
        r.mount("http://", a)
        resp = r.post(url = URL, auth = ("karaf", "karaf"))
        if not resp.ok:
            raise RuntimeError("cannot enable application")


class Onos(Node):
    def __init__(self, name):

        super().__init__(name = name,
                         type = NodeType.CONTROLLER,
                         image = "vsdn/onos",
                         services = {'6653/tcp': None,
                                     '6640/tcp': None,
                                     '8181/tcp': None,
                                     '8101/tcp': None,
                                     '9876/tcp': None},
                         cap_add = ["SYS_ADMIN", "NET_ADMIN"],
                         volume = {"/sys/fs/cgroup": {"bind": "/sys/fs/cgroup", "mode": "ro"}})

    def create(self):
        ret = DockerApi.create_node(name = self.name, image = self.image, ports = self.services,
                                    cap_add = self.cap_add, volumes = self.volume)
        if ret is not True:
            logger.error("the onos controller node cannot be created")

    def delete(self):
        ret = DockerApi.delete_node(name = self.name)
        if ret is not True:
            logger.error("the onos controller node cannot be deleted")

    def enableApp(self, app_name):
        ctl_ip = DockerApi.get_control_ip(name = self.name)
        try:
            _enable_app(ctl_ip = ctl_ip, name_app = app_name)
        except Exception as ex:
            logger.error(str(ex.args[0]))

    def disableApp(self, app_name):
        ctl_ip = DockerApi.get_control_ip(name = self.name)
        try:
            _disable_app(ctl_ip = ctl_ip, name_app = app_name)
        except Exception as ex:
            logger.error(str(ex.args[0]))
