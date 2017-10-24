import docker
import pyroute2
import ipaddress


_dockerClient = docker.from_env()
_ipCmdClient = pyroute2.IPRoute()


class ApiNode(object):
    @staticmethod
    def nodeCreate(name = None, type = None, service = None):
        if name is None:
            raise AttributeError("the name attribute cannot be null")
        elif type is None:
            raise AttributeError("the type attribute cannot be null")

        _dockerClient.containers \
            .run(image = type,
                 hostname = name,
                 name = name,
                 ports = service,
                 detach = True,
                 tty = True,
                 stdin_open = True,
                 privileged = True)

    @staticmethod
    def nodeDelete(name = None):
        if name is None:
            raise AttributeError("the name attribute cannot be null")

        container = _dockerClient.containers.get(name)
        container.stop()
        container.remove()

    @staticmethod
    def nodeStatusPause(name = None):
        if name is None:
            raise AttributeError("the name attribute cannot be null")

        container = _dockerClient.containers.get(name)
        container.pause()

    @staticmethod
    def nodeStatusResume(name = None):
        if name is None:
            raise AttributeError("the name attribute cannot be null")

        container = _dockerClient.containers.get(name)
        container.unpause()

    @staticmethod
    def nodeGetStatus(name = None):
        if name is None:
            raise AttributeError("the name attribute cannot be null")

        container = _dockerClient.containers.get(name)
        return container.status

    @staticmethod
    def nodeGetPid(name = None):
        if name is None:
            raise AttributeError("the name attribute cannot be null")

        container = _dockerClient.containers.get(name)
        return container.attrs["State"]["Pid"]

    @staticmethod
    def nodeGetIPMngt(name = None):
        if name is None:
            raise AttributeError("the name attribute cannot be null")

        container = _dockerClient.containers.get(name)
        return container.attrs['NetworkSettings']['IPAddress']

    @staticmethod
    def nodeSendCmd(name = None, cmd = None):
        if cmd is None or name is None:
            raise AttributeError("the name or command attribute cannot be null")

        container = _dockerClient.containers.get(name)
        ret = container.exec_run(cmd = cmd, tty = True, privileged = True)

        return ret

    @staticmethod
    def nodeGetServicePortExposed(name = None, port = None):
        if name is None or port is None:
            raise AttributeError("the name or port attribute cannot be null")

        container = _dockerClient.containers.get(name)
        return container.attrs['NetworkSettings']['Ports'][port + "/tcp"][0]['HostPort']


class ApiInterface(object):
    @staticmethod
    def intfExistBridge(name = None, bridge = None):
        if bridge and name is None:
            raise AttributeError("the bridge or name attribute cannot be null")

        cmd_get = "ovs-vsctl list-br"
        ret = ApiNode.nodeSendCmd(name = name, cmd = cmd_get)
        ret = ret.decode().splitlines()
        if bridge in ret:
            return True
        else:
            return False

    @staticmethod
    def intfExistInterfaceOnBridge(name = None, bridge = "switch0", port = None):
        if bridge is None or name is None or port is None:
            raise AttributeError("the bridge, name or port attributes cannot be null")

        cmd_get = "ovs-vsctl list-ports {bridge}".format(bridge = bridge)
        ret = ApiNode.nodeSendCmd(name = name, cmd = cmd_get)
        ret = ret.decode().splitlines()

        if port in ret:
            return True
        else:
            return False

    @staticmethod
    def intfAddInterfaceToBridge(name = None, port = None, index = None, bridge = "switch0"):

        if name is None:
            raise AttributeError("the name attribute cannot be null")
        elif bridge is None:
            raise AttributeError("the bridge attribute cannot be null")
        elif port is None:
            raise AttributeError("the port attribute cannot be null")

        cmd_add = "ovs-vsctl add-port {bridge} {port} -- set Interface {port} type=system".format(bridge = bridge,
                                                                                                  port = port)
        if index is not None:
            cmd_add = cmd_add + " ofport={idx}".format(idx = index)

        if ApiInterface.intfExistInterfaceOnBridge(name = name, bridge = bridge, port = port):
            raise AttributeError("the port already has included on bridge")

        ret = ApiNode.nodeSendCmd(name = name, cmd = cmd_add)
        if len(ret) != 0:
            raise ValueError(ret.decode())

    @staticmethod
    def intfConfgAddressInterface(name = None, ifname = None, ip = None, mask = None):
        if ifname is None:
            raise AttributeError("the ifname attribute cannot be null")
        elif ip is None:
            raise AttributeError("the ip attribute cannot be null")
        elif mask is None:
            raise AttributeError("the mask attribute cannot be null")

        try:
            ipaddress.ip_address(address = ip)
            ipaddress.ip_address(address = mask)
        except ValueError as ex:
            raise AttributeError(ex.args[0])

        cmd_add = "ip addr add {ip}/{mask} dev {ifname}".format(ifname = ifname, ip = ip, mask = mask)

        ret = ApiNode.nodeSendCmd(name = name, cmd = cmd_add)

        if len(ret) != 0:
            raise ValueError(ret.decode)

    @staticmethod
    def intfRemoveInterfaceFromBridge(name = None, port = None, bridge = "switch0"):
        if name is None:
            raise AttributeError("the name attribute cannot be null")
        elif bridge is None:
            raise AttributeError("the bridge attribute cannot be null")
        elif port is None:
            raise AttributeError("the port attribute cannot be null")

        cmd_del = "ovs-vsctl del-port {bridge} {port}".format(bridge = bridge, port = port)

        if not ApiInterface.intfExistInterfaceOnBridge(name = name, port = port):
            raise AttributeError("the port not exit on bridge")

        ret = ApiNode.nodeSendCmd(name = name, cmd = cmd_del)

        if len(ret) != 0:
            raise ValueError(ret.decode())


class ApiLink(object):

    @staticmethod
    def linkCreateVethPeerInterfaces(ifname_src = None, ifname_dst = None):
        if ifname_src is None or ifname_dst is None:
            raise AttributeError("the port name source or destination attributes cannot be null")

        _ipCmdClient.link('add', ifname = ifname_src, peer = ifname_dst, kind = 'veth')

        idx_if_src = _ipCmdClient.link_lookup(ifname = ifname_src)[0]
        idx_if_dst = _ipCmdClient.link_lookup(ifname = ifname_dst)[0]

        _ipCmdClient.link('set', index = idx_if_src, mtu = 9000)
        _ipCmdClient.link('set', index = idx_if_src, state = 'up')

        _ipCmdClient.link('set', index = idx_if_dst, mtu = 9000)
        _ipCmdClient.link('set', index = idx_if_dst, state = 'up')

    @staticmethod
    def linkVethPairingNodes(name_src = None, name_dst = None, ifname_src = None, ifname_dst = None):

        if name_src is None or name_dst is None:
            raise AttributeError("the node name source or destination attributes cannot be null")
        elif ifname_src is None or ifname_dst is None:
            raise AttributeError("the interface name source or destination attributes cannot be null")

        pid_src = ApiNode.nodeGetPid(name_src)
        pid_dst = ApiNode.nodeGetPid(name_dst)

        idx_if_src = _ipCmdClient.link_lookup(ifname = ifname_src)[0]
        idx_if_dst = _ipCmdClient.link_lookup(ifname = ifname_dst)[0]

        _ipCmdClient.link('set', index = idx_if_src, net_ns_pid = pid_src, state = "up")
        _ipCmdClient.link('set', index = idx_if_dst, net_ns_pid = pid_dst, state = "up")

    @staticmethod
    def linkVethUnpairingNodes(name_src = None, name_dst = None, ifname_src = None, ifname_dst = None):

        if name_src is None or name_dst is None:
            raise AttributeError("the node name source or destination attributes cannot be null")
        elif ifname_src is None or ifname_dst is None:
            raise AttributeError("the interface name source or destination attributes cannot be null")

        cmd_del_port = "ip link del {port}".format(port = ifname_src)

        container = _dockerClient.containers.get(name_src)
        ret = container.exec_run(cmd = cmd_del_port, tty = True, privileged = True)

        if len(ret) != 0:
            raise ValueError(ret.decode())


class ApiService(object):
    @staticmethod
    def serviceSetNodeManager(name = None, port = "6640", protocol = "ptcp"):
        if name is None:
            raise AttributeError("the name attribute cannot be null")

        cmd_set_manager = "ovs-vsctl set-manager {protocol}:{port}".format(protocol = protocol, port = port)
        ret = ApiNode.nodeSendCmd(name = name, cmd = cmd_set_manager)

        if len(ret) != 0:
            raise ValueError(ret.decode())

    @staticmethod
    def serviceDelNodeManager(name = None):
        if name is None:
            raise AttributeError("the name attribute cannot be null")

        cmd_del_manager = "ovs-vsctl del-manager"
        ret = ApiNode.nodeSendCmd(name = name, cmd = cmd_del_manager)

        if len(ret) != 0:
            raise ValueError(ret.decode())

    @staticmethod
    def serviceSetNodeController(name = None, ip = None, port = "6653", bridge = "switch0"):
        if name is None or ip is None:
            raise AttributeError("the name or ip attribute cannot be null")

        cmd_set_controller = "ovs-vsctl set-controller {bridge} tcp:{ip}:{port}"
        ret = ApiNode.nodeSendCmd(name = name, cmd = cmd_set_controller.format(ip = ip, bridge = bridge, port = port))

        if len(ret) != 0:
            raise ValueError(ret.decode)

    @staticmethod
    def serviceDelNodeController(name = None, bridge = "swtich0"):
        if name is None:
            raise AttributeError("the name attribute cannot be null")

        cmd_del_controller = "ovs-vsctl del-controller {bridge} "

        ret = ApiNode.nodeSendCmd(name = name, cmd = cmd_del_controller.format(bridge = bridge))

        if len(ret) != 0:
            raise ValueError(ret.decode)
