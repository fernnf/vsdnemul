import os
from Api.utils import check_not_null
from Api.Docker.docker_node import _exec


def set_manager(name, ip = None, type = "tcp", port = "6640"):
    check_not_null(name, "The name container cannot be null")
    check_not_null(ip, "the ip cannot be null")

    ovsctl = "/usr/bin/ovs-vsctl"

    if os.path.exists(ovsctl):
      cmd_set_mgt="{ctl} set-manager {type}:{ip}:{port}".format(ctl = ovsctl, type = type, ip = ip, port = port)
      ret = _exec(name = name, cmd = cmd_set_mgt)



