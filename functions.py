import docker
import pyroute2

_client = docker.from_env()
_ip = pyroute2.IPRoute()


def create_node(**kwargs):
    node_name = None
    node_type = None
    node_vol = None  # optional
    node_svc = None  # optional

    if kwargs.get("name"):
        node_name = kwargs["name"]
    else:
        raise ValueError("the name attribute cannot be null")

    if kwargs.get("type"):
        node_type = kwargs["type"]
    else:
        raise ValueError("the type attribute cannot be null")

    if kwargs.get("service"):
        node_svc = kwargs["service"]

    if kwargs.get("volume"):
        node_vol = kwargs["volume"]

    container = _client.containers.run(image = node_type, hostname = node_name, name = node_name, volumes = node_vol,
                                       ports = node_svc, detach = True, tty = True, stdin_open = True,
                                       privileged = True)


def delete_node(name = None):
    if name is None:
        raise AttributeError("the name attribute cannot be null")

    container = _client.containers.get(name)
    container.stop()
    container.remove()


def get_status_node(name = None):
    if name is None:
        raise AttributeError("the name attribute cannot be null")

    container = _client.containers.get(name)
    return container.status


def get_pid_node(name = None):
    if name is None:
        raise AttributeError("the name attribute cannot be null")

    container = _client.containers.get(name)
    return container.attrs["State"]["Pid"]


def get_ip_mgt_node(name = None):
    if name is None:
        raise AttributeError("the name attribute cannot be null")

    container = _client.containers.get(name)
    return container.attrs['NetworkSettings']['IPAddress']


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


def set_bridge_oper_node(**kwargs):
    cmd_create = "ovs-vsctl add-br {bridge} -- set Bridge {bridge} datapath_type=netdev"

    if kwargs.get("name"):
        raise AttributeError("the name attribute cannot be null")

    if kwargs.get("bridge"):
        cmd_create = cmd_create.format(bridge = kwargs["bridge"])
    else:
        raise AttributeError("the bridge attribute cannot be null")

    if kwargs.get("protocols"):
        cmd_create = cmd_create + " protocols={of_version}".format(of_version = kwargs["protocols"])

    if kwargs.get("dpid"):
        cmd_create = cmd_create + " other-config:datapath-id={dpid}".format(dpid = kwargs["dpid"])

    if exist_br(name = kwargs["name"], bridge = kwargs["bridge"]):
        raise AttributeError("the bridge oper already has created in node")

    container = _client.containers.get(kwargs["name"])
    container.exec_run(cmd = cmd_create, tty = True, privileged = True)


def exist_port(name = None, bridge = None, port = None):
    if bridge and name and port is None:
        raise AttributeError("the bridge, name or port attributes cannot be null")

    cmd_get = "ovs-vsctl list-ports {bridge}".format(bridge = bridge)
    container = _client.containers.get(name)

    ret = container.exec_run(cmd = cmd_get, tty = True, privileged = True)
    ret = ret.decode().splitlines()

    if port in ret:
        return True
    else:
        return False


def add_port_to_bridge_oper(**kwargs):
    cmd_add = "ovs-vsctl add-port {bridge} {port} -- set Interface {port}"

    if kwargs.get("name"):
        raise AttributeError("the name node attribute cannot be null")

    if kwargs.get("bridge") and kwargs.get("port"):
        cmd_add = cmd_add.format(bridge = kwargs["bridge"], port = kwargs["port"])

    else:
        raise AttributeError("the bridge or port attribute cannot be null")

    if kwargs.get("index"):
        cmd_add = cmd_add + " of_port={idx}".format(idx = kwargs["index"])

    if exist_port(name = kwargs["name"], bridge = kwargs["bridge"], port = kwargs["port"]):
        raise AttributeError("the port already has included on bridge oper")

    container = _client.containers.get(kwargs["name"])
    container.exec_run(cmd = cmd_add, tty = True, privileged = True)


def create_eth_link_ports(ifname_src = None, ifname_dst = None):
    if ifname_src and ifname_dst is None:
        raise AttributeError("the port name source or destination attributes cannot be null")

    _ip.link('add', ifname = ifname_src, peer = ifname_dst, kind = 'veth')

    ifsrc = _ip.link_lookup(ifname = ifname_src)[0]
    ifdst = _ip.link_lookup(ifname = ifname_dst)[0]

    _ip.link('set', index = ifsrc, mtu = 9000)
    _ip.link('set', index = ifsrc, state = 'up')

    _ip.link('set', index = ifdst, mtu = 9000)
    _ip.link('set', index = ifdst, state = 'up')


def create_link_node(**kwargs):
    if kwargs.get("node_src") and kwargs.get("node_dst"):
        raise AttributeError("the node name source or destination attributes cannot be null")

    create_eth_link_ports(ifname_dst = kwargs["ifname_dst"], ifname_src = kwargs["ifname_src"])

    pid_src = get_pid_node(kwargs["node_src"])
    pid_dst = get_pid_node(kwargs["node_dst"])

    idx_src = _ip.link_lookup(ifname = kwargs["ifname_dst"])[0]
    idx_dst = _ip.link_lookup(ifname = kwargs["ifname_src"])[0]

    _ip.link('set', index = idx_src, net_ns_pid = pid_src)
    _ip.link('set', index = idx_dst, net_ns_pid = pid_dst)


def delete_link_node(**kwargs):
    if kwargs.get("node_src") and kwargs.get("node_dst"):
        raise AttributeError("the node name source or destination attributes cannot be null")