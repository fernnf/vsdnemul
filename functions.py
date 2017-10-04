import docker
import pyroute2

_client = docker.from_env()
_ip = pyroute2.IPRoute()


class ApiNode(object):
    @staticmethod
    def create_node(name = None, type = None, service = None):
        if name is None:
            raise AttributeError("the name attribute cannot be null")
        elif type is None:
            raise AttributeError("the type attribute cannot be null")

        _client.containers \
            .run(image = type,
                 hostname = name,
                 name = name,
                 ports = service,
                 detach = True,
                 tty = True,
                 stdin_open = True,
                 privileged = True)

    @staticmethod
    def delete_node(name = None):
        if name is None:
            raise AttributeError("the name attribute cannot be null")

        container = _client.containers.get(name)
        container.stop()
        container.remove()

    @staticmethod
    def pause_node(name = None):
        if name is None:
            raise AttributeError("the name attribute cannot be null")

        container = _client.containers.get(name)
        container.pause()

    @staticmethod
    def resume_node(name = None):
        if name is None:
            raise AttributeError("the name attribute cannot be null")

        container = _client.containers.get(name)
        container.unpause()

    @staticmethod
    def get_status(name = None):
        if name is None:
            raise AttributeError("the name attribute cannot be null")

        container = _client.containers.get(name)
        return container.status

    @staticmethod
    def get_pid(name = None):
        if name is None:
            raise AttributeError("the name attribute cannot be null")

        container = _client.containers.get(name)
        return container.attrs["State"]["Pid"]

    @staticmethod
    def get_ip_mgt(name = None):
        if name is None:
            raise AttributeError("the name attribute cannot be null")

        container = _client.containers.get(name)
        return container.attrs['NetworkSettings']['IPAddress']

    @staticmethod
    def exec_cmd(name = None, cmd = None):
        if cmd is None or name is None:
            raise AttributeError("the name or command attribute cannot be null")

        container = _client.containers.get(name)
        ret = container.exec_run(cmd = cmd, tty = True, privileged = True)

        return ret

    @staticmethod
    def port_exposed(name = None, port = None):
        if name is None or port is None:
            raise AttributeError("the name or port attribute cannot be null")

        container = _client.containers.get(name)
        return container.attrs['NetworkSettings']['Ports'][port + "/tcp"][0]['HostPort']


class ApiInterface(object):
    @staticmethod
    def exist_br(name = None, bridge = None):
        if bridge and name is None:
            raise AttributeError("the bridge or name attribute cannot be null")

        cmd_get = "ovs-vsctl list-br"
        ret = ApiNode.exec_cmd(name = name, cmd = cmd_get)
        ret = ret.decode().splitlines()
        if bridge in ret:
            return True
        else:
            return False

    @staticmethod
    def exist_port(name = None, bridge = "switch0", port = None):
        if bridge is None or name is None or port is None:
            raise AttributeError("the bridge, name or port attributes cannot be null")

        cmd_get = "ovs-vsctl list-ports {bridge}".format(bridge = bridge)
        ret = ApiNode.exec_cmd(name = name, cmd = cmd_get)
        ret = ret.decode().splitlines()

        if port in ret:
            return True
        else:
            return False

    @staticmethod
    def add_port_to_bridge(name = None, port = None, index = None, bridge = "switch0"):

        if name is None:
            raise AttributeError("the name attribute cannot be null")
        elif bridge is None:
            raise AttributeError("the bridge attribute cannot be null")
        elif port is None:
            raise AttributeError("the port attribute cannot be null")

        cmd_add = "ovs-vsctl add-port {bridge} {port} -- set Interface {port} type=system"
        cmd_add = cmd_add.format(bridge = bridge, port = port)

        if index is not None:
            cmd_add = cmd_add + " ofport={idx}".format(idx = index)

        if ApiInterface.exist_port(name = name, bridge = bridge, port = port):
            raise AttributeError("the port already has included on bridge oper")

        ret = ApiNode.exec_cmd(name = name, cmd = cmd_add)
        if len(ret) != 0:
            raise ValueError(ret.decode())

    @staticmethod
    def conf_addr_to_port(name = None, ifname = None, ip = None, mask = None):
        if ifname is None:
            raise AttributeError("the ifname attribute cannot be null")
        elif ip is None:
            raise AttributeError("the ip attribute cannot be null")
        elif mask is None:
            raise AttributeError("the mask attribute cannot be null")

        cmd_add = "ip addr add {ip}/{mask} dev {ifname}"
        cmd_add = cmd_add.format(ifname = ifname, ip = ip, mask = mask)

        ret = ApiNode.exec_cmd(name = name, cmd = cmd_add)

        if len(ret) !=0:
            raise ValueError(ret.decode)

    @staticmethod
    def del_port_from_bridge(name = None, port = None, bridge = "switch0"):

        if name is None:
            raise AttributeError("the name attribute cannot be null")
        elif bridge is None:
            raise AttributeError("the bridge attribute cannot be null")
        elif port is None:
            raise AttributeError("the port attribute cannot be null")

        cmd_del = "ovs-vsctl del-port {bridge} {port}"
        cmd_del = cmd_del.format(bridge = bridge, port = port)

        if not ApiInterface.exist_port(name = name, port = port):
            raise AttributeError("the port not exit on bridge")

        ret = ApiNode.exec_cmd(name = name, cmd = cmd_del)

        if len(ret) != 0:
            raise ValueError(ret.decode())


class ApiLink(object):
    @staticmethod
    def create_veth_peer_link(ifname_src = None, ifname_dst = None):
        if ifname_src is None or ifname_dst is None:
            raise AttributeError("the port name source or destination attributes cannot be null")

        _ip.link('add', ifname = ifname_src, peer = ifname_dst, kind = 'veth')

        idx_if_src = _ip.link_lookup(ifname = ifname_src)[0]
        idx_if_dst = _ip.link_lookup(ifname = ifname_dst)[0]

        _ip.link('set', index = idx_if_src, mtu = 9000)
        _ip.link('set', index = idx_if_src, state = 'up')

        _ip.link('set', index = idx_if_dst, mtu = 9000)
        _ip.link('set', index = idx_if_dst, state = 'up')

    @staticmethod
    def create_link_node(name_src = None, name_dst = None, ifname_src = None, ifname_dst = None):

        if name_src is None or name_dst is None:
            raise AttributeError("the node name source or destination attributes cannot be null")
        elif ifname_src is None or ifname_dst is None:
            raise AttributeError("the interface name source or destination attributes cannot be null")

        ApiLink.create_veth_peer_link(ifname_src = ifname_src, ifname_dst = ifname_dst)

        pid_src = ApiNode.get_pid(name_src)
        pid_dst = ApiNode.get_pid(name_dst)

        idx_if_src = _ip.link_lookup(ifname = ifname_src)[0]
        idx_if_dst = _ip.link_lookup(ifname = ifname_dst)[0]

        _ip.link('set', index = idx_if_src, net_ns_pid = pid_src, state = "up")
        _ip.link('set', index = idx_if_dst, net_ns_pid = pid_dst, state = "up")

    @staticmethod
    def delete_link_node(name_src = None, name_dst = None, ifname_src = None, ifname_dst = None):

        if name_src is None or name_dst is None:
            raise AttributeError("the node name source or destination attributes cannot be null")
        elif ifname_src is None or ifname_dst is None:
            raise AttributeError("the interface name source or destination attributes cannot be null")

        cmd_del_port = "ip link del {port}"

        container = _client.containers.get(name_src)
        ret = container.exec_run(cmd = cmd_del_port.format(port = ifname_src), tty = True, privileged = True)

        if len(ret) != 0:
            raise ValueError(ret.decode())


class ApiService(object):
    @staticmethod
    def setManager(name = None):
        if name is None:
            raise AttributeError("the name attribute cannot be null")

        cmd_set_manager = "ovs-vsctl set-manager ptcp:6640"
        ret = ApiNode.exec_cmd(name = name, cmd = cmd_set_manager)

        if len(ret) != 0:
            raise ValueError(ret.decode())

    @staticmethod
    def setController(name = None, ip = None, port = "6653", bridge = "switch0"):
        if name is None or ip is None:
            raise AttributeError("the name or ip attribute cannot be null")

        cmd_set_controller = "ovs-vsctl set-controller {bridge} tcp:{ip}:{port}"
        ret = ApiNode.exec_cmd(name = name, cmd = cmd_set_controller.format(ip = ip, bridge = bridge, port = port))

        if len(ret) != 0:
            raise ValueError(ret.decode)
