import docker
import pyroute2

_client = docker.from_env()
_ip = pyroute2.IPRoute()


class ApiNode(object):
    @staticmethod
    def create_node(**kwargs):
        attrs = {
            "name": None,  # mandatory
            "type": None,  # mandatory
            "service": None,  # optional
            "volume": None  # optional
        }
        attrs.update(kwargs)

        if attrs["name"] is None:
            raise AttributeError("the name attribute cannot be null")
        elif attrs["type"] is None:
            raise AttributeError("the type attribute cannot be null")

        _client.containers \
            .run(image = attrs.get("type"),
                 hostname = attrs.get("name"),
                 name = attrs.get("name"),
                 volumes = attrs.get("volume"),
                 ports = attrs.get("service"),
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
    def get_status_node(name = None):
        if name is None:
            raise AttributeError("the name attribute cannot be null")

        container = _client.containers.get(name)
        return container.status

    @staticmethod
    def get_pid_node(name = None):
        if name is None:
            raise AttributeError("the name attribute cannot be null")

        container = _client.containers.get(name)
        return container.attrs["State"]["Pid"]

    @staticmethod
    def get_ip_mgt_node(name = None):
        if name is None:
            raise AttributeError("the name attribute cannot be null")

        container = _client.containers.get(name)
        return container.attrs['NetworkSettings']['IPAddress']


class ApiInterface(object):
    @staticmethod
    def exist_br(name = None, bridge = None):
        if bridge and name is None:
            raise AttributeError("the bridge or name attribute cannot be null")

        cmd_get = "ovs-vsctl list-br"
        container = _client.containers.get(name)

        ret = container.exec_run(cmd = cmd_get, tty = True, privileged = True)
        ret = ret.decode().splitlines()

        if bridge in ret:
            return True
        else:
            return False

    @staticmethod
    def set_bridge_oper_node(**kwargs):
        attrs = {
            "name": None,  # mandatory
            "bridge": None,  # mandatory
            "protocols": "OpenFlow13",  # optional
            "dpid": None  # optional
        }
        attrs.update(kwargs)

        # Mandatory
        if attrs.get("name") is None:
            raise AttributeError("the name attribute cannot be null")
        elif attrs.get("bridge") is None:
            raise AttributeError("the bridge attribute cannot be null")

        cmd_create = "ovs-vsctl add-br {bridge} -- set Bridge {bridge} datapath_type=netdev"
        cmd_create = cmd_create.format(bridge = attrs.get("bridge"))

        # Optional
        if attrs["protocols"] is not None:
            cmd_create = cmd_create + " protocols={of_version}".format(of_version = attrs.get("protocols"))
        # Optional
        if attrs["dpid"] is not None:
            cmd_create = cmd_create + " other-config:datapath-id={dpid}".format(dpid = attrs.get("dpid"))
        # Optional
        if ApiInterface.exist_br(name = attrs.get("name"), bridge = attrs.get("bridge")):
            raise AttributeError("the bridge oper already has created in node")

        container = _client.containers.get(attrs.get("name"))
        container.exec_run(cmd = cmd_create, tty = True, privileged = True)

    @staticmethod
    def exist_port(name = None, bridge = None, port = None):
        if bridge or name or port is None:
            raise AttributeError("the bridge, name or port attributes cannot be null")

        cmd_get = "ovs-vsctl list-ports {bridge}".format(bridge = bridge)
        container = _client.containers.get(name)

        ret = container.exec_run(cmd = cmd_get, tty = True, privileged = True)
        ret = ret.decode().splitlines()

        if port in ret:
            return True
        else:
            return False

    @staticmethod
    def add_port_to_bridge_oper(**kwargs):

        attrs = {
            "name": None,  # mandatory
            "bridge": None,  # mandatory
            "port": None,  # mandatory
            "index": None  # optional
        }

        attrs.update(kwargs)

        if attrs["name"] is None:
            raise AttributeError("the name attribute cannot be null")
        elif attrs["bridge"] is None:
            raise AttributeError("the bridge attribute cannot be null")
        elif attrs["port"] is None:
            raise AttributeError("the port attribute cannot be null")

        cmd_add = "ovs-vsctl add-port {bridge} {port} -- set Interface {port}"
        cmd_add = cmd_add.format(bridge = attrs.get("bridge"), port = attrs.get("port"))

        if attrs["index"] is not None:
            cmd_add = cmd_add + " of_port={idx}".format(idx = attrs.get("index"))

        if ApiInterface.exist_port(name = attrs.get("name"), bridge = attrs.get("bridge"), port = attrs.get("port")):
            raise AttributeError("the port already has included on bridge oper")

        container = _client.containers.get(attrs.get("name"))
        container.exec_run(cmd = cmd_add, tty = True, privileged = True)


class ApiLink(object):
    @staticmethod
    def create_eth_link_ports(ifname_src = None, ifname_dst = None):
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
    def create_link_node(**kwargs):
        attrs = {
            "name_src": None,  # mandatory
            "name_dst": None,  # mandatory
            "ifname_src": None,  # mandatory
            "ifname_dst": None  # mandatory
        }
        attrs.update(kwargs)

        if attrs["name_src"] is None or attrs["name_dst"] is None:
            raise AttributeError("the node name source or destination attributes cannot be null")
        elif attrs["ifname_src"] is None or attrs["ifname_dst"]:
            raise AttributeError("the interface name source or destination attributes cannot be null")

        ApiLink.create_eth_link_ports(ifname_dst = attrs.get("ifname_dst"), ifname_src = attrs.get("ifname_src"))

        pid_src = ApiNode.get_pid_node(attrs.get("node_src"))
        pid_dst = ApiNode.get_pid_node(attrs.get("node_dst"))

        idx_if_src = _ip.link_lookup(ifname = attrs.get("ifname_dst"))[0]
        idx_if_dst = _ip.link_lookup(ifname = attrs.get("ifname_src"))[0]

        _ip.link('set', index = idx_if_src, net_ns_pid = pid_src)
        _ip.link('set', index = idx_if_dst, net_ns_pid = pid_dst)

    @staticmethod
    def delete_link_node(**kwargs):
        attrs = {
            "bridge": None,  # mandatory
            "name_src": None,  # mandatory
            "name_dst": None,  # mandatory
            "ifname_src": None,  # mandatory
            "ifname_dst": None  # mandatory
        }
        attrs.update(kwargs)

        if attrs["name_src"] is None or attrs["name_dst"] is None:
            raise AttributeError("the node name source or destination attributes cannot be null")
        elif attrs["ifname_src"] is None or attrs["ifname_dst"] is None:
            raise AttributeError("the interface name source or destination attributes cannot be null")
        elif attrs["bridge"] is None:
            raise AttributeError("the bridge name source or destination attributes cannot be null")

        if not ApiInterface.exist_port(name = attrs["name_src"], bridge = attrs["bridge"], port = attrs["ifname_src"]):
            AttributeError("the interface name source or destination attributes not exist")

        if not ApiInterface.exist_port(name = attrs["name_dst"], bridge = attrs["bridge"], port = attrs["ifname_dst"]):
            AttributeError("the interface name source or destination attributes not exist")

        cmd_del = "ip link del {port}".format(port = attrs["ifname_src"])

        container = _client.containers.get(attrs["name_src"])
        container.exec_run(cmd = cmd_del, tty = True, privileged = True)


if __name__ == '__main__':
    name = "node23"  # mandatory
    type = "sdnoverlay/whitebox"  # mandatory
    service = {'22/tcp': None, '6633/tcp': None, '6640/tcp': None, '6653/tcp': None}  # optional
    volume = {'/sys/fs/cgroup': {'bind': '/sys/fs/cgroup', 'mode': 'ro'}}  # optional

    ApiNode.create_node(name = name, type = type, service = service, volume = volume)

    status = ""


    print(ApiNode.get_status_node(name))
