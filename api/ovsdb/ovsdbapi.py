import os
import subprocess

from pathlib import Path
from api.docker.dockerapi import DockerApi
from api.log.logapi import logging
from api.utils import check_not_null

logger = logging.getLogger("OvsdbApi")


def _exec_action(ctl, cmd, netns = None):
    check_not_null(ctl, "the binary cannot be null")
    check_not_null(cmd, "the frontend cannot be null")

    if netns is None:
        ret = subprocess.Popen(cmd, shell = True)
        ret.wait()

        if ret.returncode is not 0:
            outs, errs = ret.communicate(timeout = 15)
            raise RuntimeError("{err}".format(err = errs.decode()))
    else:
        ret = DockerApi.run_cmd(name = netns, cmd = cmd)
        if len(ret) is not 0:
            raise RuntimeError("{err}".format(err = ret.decode()))


def _set_manager(ip, netns = None, type = "tcp", port = "6640"):
    check_not_null(ip, "the ip cannot be null")

    ovsctl = Path("/usr/bin/ovs-vsctl")
    cmd_set_mgt = "{ctl} set-manager {type}:{ip}:{port}".format(ctl = ovsctl.as_posix(),
                                                                type = type,
                                                                ip = ip,
                                                                port = port)

    _exec_action(ctl = ovsctl, cmd = cmd_set_mgt, netns = netns)


def _del_manager(netns = None):
    ovsctl = Path("/usr/bin/ovs-vsctl")

    cmd_del_mgt = "{ctl} del-controller".format(ctl = ovsctl.as_posix())

    _exec_action(ctl = ovsctl, cmd = cmd_del_mgt, netns = netns)


def _set_controller(ip, bridge, netns = None, type = "tcp", port = "6653"):
    check_not_null(ip, "the ip cannot be null")
    check_not_null(bridge, "the bridge name cannot be null")

    ovsctl = Path("/usr/bin/ovs-vsctl")

    cmd_set_ctl = "{ctl} set-controller {bridge} {type}:{ip}:{port}".format(ctl = ovsctl.as_posix(), bridge = bridge,
                                                                            type = type, ip = ip, port = port)
    _exec_action(ctl = cmd_set_ctl, cmd = cmd_set_ctl, netns = netns)


def _del_controller(bridge, netns = None):
    check_not_null(bridge, "the bridge name cannot be null")
    ovsctl = Path("/usr/bin/ovs-vsctl")

    cmd_del_ctl = "{ctl} del-controller {bridge}".format(ctl = ovsctl.as_posix(), bridge = bridge)

    _exec_action(ctl = ovsctl, cmd = cmd_del_ctl, netns = netns)


def _set_bridge(bridge, netns = None, dpid = None, of_ver = "OpenFlow13", dp_type = "netdev"):
    check_not_null(bridge, "the bridge name cannot be null")
    ovsctl = Path("/usr/bin/ovs-vsctl")

    cmd_set_bridge = "{ctl} add-br {bridge} -- set bridge {bridge} datapath_type={dp_type} protocols={version} ".format(
        ctl = ovsctl.as_posix(), bridge = bridge, dp_type = dp_type, version = of_ver)

    if dpid is not None:
        cmd_set_bridge = cmd_set_bridge + "other_config:datapath_id={dpid}".format(dpid = dpid)

    _exec_action(ctl = ovsctl, cmd = cmd_set_bridge, netns = netns)


def _del_bridge(bridge, netns = None):
    check_not_null(bridge, "the bridge name cannot be null")
    ovsctl = Path("/usr/bin/ovs-vsctl")

    cmd_del_bridge = "{ctl} del-br {bridge}".format(ctl = ovsctl.as_posix(), bridge = bridge)

    _exec_action(ctl = ovsctl, cmd = cmd_del_bridge, netns = netns)


def _add_port_br(bridge, port_name, netns = None):
    check_not_null(bridge, "the bridge name cannot be null")
    check_not_null(port_name, "the port name cannot be null")
    ovsctl = Path("/usr/bin/ovs-vsctl")

    if not ovsctl.is_file():
        raise RuntimeError("the command not found")

    cmd_add_port = "{ctl} add-port {bridge} {port}".format(ctl = ovsctl, bridge = bridge, port = port_name)

    _exec_action(ctl = ovsctl, cmd = cmd_add_port, netns = netns)


def _del_port_br(bridge, port_name, netns = None):
    check_not_null(bridge, "the bridge name cannot be null")
    check_not_null(port_name, "the port name cannot be null")
    ovsctl = Path("/usr/bin/ovs-vsctl")

    if not ovsctl.is_file():
        raise RuntimeError("the command not found")

    cmd_add_port = "{ctl} del-port {bridge} {port}".format(ctl = ovsctl, bridge = bridge, port = port_name)

    _exec_action(ctl = ovsctl, cmd = cmd_add_port, netns = netns)


def _add_port_ns(bridge, netns, intf_name, ip = None, gateway = None, mtu = 1500):
    check_not_null(bridge, "the bridge name cannot be null")
    check_not_null(netns, "the namespace name cannot be null")
    check_not_null(intf_name, "the interface name cannot be null")
    ovsdocker = "/usr/bin/ovs-docker"
    cmd_add_port_ns = "{ctl} add-port {bridge} {ifname} {netns} ".format(bridge = bridge,
                                                                         ctl = ovsdocker,
                                                                         ifname = intf_name,
                                                                         netns = netns)

    if ip is not None:
        cmd_add_port_ns = cmd_add_port_ns + "--ipaddress={ip} ".format(ip = ip)

    if gateway is not None:
        cmd_add_port_ns = cmd_add_port_ns + "--gateway={gate} ".format(gate = gateway)

    if mtu is not None:
        cmd_add_port_ns = cmd_add_port_ns + "--mtu={mtu} ".format(mtu = mtu)

    if DockerApi.get_status_node(name = netns) == "running":

        ret = subprocess.Popen(cmd_add_port_ns, shell = True)
        ret.wait()

        if ret.returncode is not 0:
            outs, errs = ret.communicate(timeout = 15)
            raise RuntimeError("{err}".format(err = errs.decode()))

    else:
        raise RuntimeError("the node is not running")


def _del_port_ns(bridge, netns, intf_name):
    check_not_null(bridge, "the bridge name cannot be null")
    check_not_null(netns, "the namespace name cannot be null")
    check_not_null(intf_name, "the interface name cannot be null")

    ovsdocker = "/usr/bin/ovs-docker"
    cmd_del_port_ns = "{ctl} del-port {bridge} {ifname} {netns} ".format(bridge = bridge,
                                                                         ctl = ovsdocker,
                                                                         ifname = intf_name,
                                                                         netns = netns)
    if DockerApi.get_status_node(name = netns) == "running":

        ret = subprocess.Popen(cmd_del_port_ns, shell = True)
        ret.wait()

        if ret.returncode is not 0:
            outs, errs = ret.communicate(timeout = 15)
            raise RuntimeError("error: {err}".format(err = errs.decode()))

    else:
        raise RuntimeError("the node is not running")


def _set_openflow_version(netns, bridge, version = "OpenFlow13"):
    check_not_null(value = netns, msg = "the name cannot be null")

    ovsctl = "/usr/bin/ovs-vsctl"
    cmd_set_of_version = "{ctl} set bridge {bridge} protocols={version".format(ctl = ovsctl, bridge = bridge,
                                                                               version = version)
    _exec_action(ctl = ovsctl, cmd = cmd_set_of_version)


class OvsdbApi(object):

    @staticmethod
    def set_manager(ip, netns = None, type = "tcp", port = "6640"):
        try:
            _set_manager(ip = ip, netns = netns, type = type, port = port)
            return True
        except Exception as ex:
            logger.error(str(ex.args))
            return False

    @staticmethod
    def del_manager(netns = None):
        try:
            _del_manager(netns = netns)
            return True
        except Exception as ex:
            logger.error(str(ex.args))
            return False

    @staticmethod
    def set_controller(ip, bridge, netns = None, type = "tcp", port = "6653"):
        try:
            _set_controller(ip = ip, bridge = bridge, type = type, port = port, netns = netns)
            return True
        except Exception as ex:
            logger.error(str(ex.args))
            return False

    @staticmethod
    def del_controller(bridge, netns = None):
        try:
            _del_controller(bridge = bridge, netns = netns)
            return True
        except Exception as ex:
            logger.error(str(ex.args))
            return False

    @staticmethod
    def set_bridge(bridge, netns = None, dpid = None, of_ver = "OpenFlow13", dp_type = "netdev"):
        try:
            _set_bridge(bridge = bridge, netns = netns, dpid = dpid, of_ver = of_ver, dp_type = dp_type)
            return True
        except Exception as ex:
            logger.error(str(ex.args))
            return False

    @staticmethod
    def del_bridge(bridge, netns = None):
        try:
            _del_bridge(bridge = bridge, netns = netns)
            return True
        except Exception as ex:
            logger.error(str(ex.args))
            return False

    @staticmethod
    def add_port_br(bridge, port_name, netns = None):
        try:
            _add_port_br(bridge = bridge, port_name = port_name, netns = netns)
            return True

        except Exception as ex:
            logger.error(str(ex.args))
            return False

    @staticmethod
    def del_port_br(bridge, port_name, netns = None):
        try:
            _del_port_br(bridge = bridge, port_name = port_name, netns = netns)
            return True

        except Exception as ex:
            logger.error(str(ex.args))
            return False

    @staticmethod
    def add_port_ns(bridge, netns, intf_name, ip = None, gateway = None, mtu = 1500):
        try:
            _add_port_ns(bridge = bridge, netns = netns, intf_name = intf_name, ip = ip, gateway = gateway, mtu = mtu)
            return True
        except Exception as ex:
            logger.error(str(ex.args))
            return False

    @staticmethod
    def del_port_ns(bridge, netns, intf_name):
        try:
            _del_port_ns(bridge = bridge, netns = netns, intf_name = intf_name)
            return True
        except Exception as ex:
            logger.error(str(ex.args))
            return False

    @staticmethod
    def change_openflow_version(bridge, netns, version = "OpenFlow13"):
        try:
            _set_openflow_version(netns = netns, bridge = bridge, version = version)
        except Exception as ex:
            logger.error(str(ex.args))
