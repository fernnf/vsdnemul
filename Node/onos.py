from Node.node import Node, ApiNode
from log import Logger
import requests


class Onos(Node):
    logger = Logger.logger("ONOS")

    def __init__(self, label = None):
        super().__init__(label = label,
                         type = "ONOS Controller",
                         image = "vsdn/onos",
                         service = {'6653/tcp': None,
                                    '6640/tcp': None,
                                    '8181/tcp': None,
                                    '8101/tcp': None,
                                    '9876/tcp': None},
                         volume = {"/sys/fs/cgroup": {"bind": "/sys/fs/cgroup", "mode": "ro"}})

    def create(self):
        try:
            return ApiNode.create_node(label = self.label, image = self.image, service = self.service,
                                       volume = self.volume, cap_add = self.cap_add)
        except Exception as ex:
            self.logger.error(ex.args[0])

    def delete(self):
        try:
            return ApiNode.delete_node(label = self.label)
        except Exception as ex:
            self.logger.error(str(ex.args))

    def enableApp(self, appName):
        try:
            ApiOnos.enableApp(ctl_ip = self.control_ip, nameApp = appName)
        except Exception as ex:
            self.logger.error(str(ex.args))

    def disableApp(self, appName):
        try:
            ApiOnos.disableApp(ctl_ip = self.control_ip, nameApp = appName)
        except Exception as ex:
            self.logger.error(str(ex.args))


class ApiOnos(object):
    logger = Logger.logger("ApiONOS")

    @staticmethod
    def enableApp(ctl_ip, nameApp):
        URL = "http://{addr}:8181/onos/v1/applications/{app}/active".format(addr = ctl_ip, app = nameApp)

        with requests.Session() as r:
            a = requests.adapters.HTTPAdapter(max_retries = 10)
            r.mount("http://", a)
            resp = r.post(url = URL, auth = ("karaf", "karaf"))
            if not resp.ok:
                raise RuntimeError("cannot enable application")


    @staticmethod
    def disableApp(ctl_ip, nameApp):
        URL = "http://{addr}:8181/onos/v1/applications/{app}/active".format(addr = ctl_ip, app = nameApp)
        with requests.Session() as r:
            a = requests.adapters.HTTPAdapter(max_retries = 10)
            r.mount("http://", a)
            resp = r.delete(url = URL, auth = ("karaf", "karaf"))
            if not resp.ok:
                raise RuntimeError("cannot disable application")
