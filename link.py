from utils import check_not_null, create_veth_link_containers, delete_veth_link_containers, config_interface_address
import uuid

class Link(object):
    def __init__(self, type, node_source = None, node_target = None):
        self.node_source = node_source
        self.node_target = node_target
        self.type = type
        self.__id = uuid.uuid4()

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, value):
        pass

    @property
    def node_source(self):
        return self.__node_source

    @node_source.setter
    def node_source(self, value):
        self.__node_source = check_not_null(value = value, msg = "the label of source node cannot be null")

    @property
    def node_target(self):
        return self.__node_target

    @node_target.setter
    def node_target(self, value):
        self.__node_target = check_not_null(value = value, msg = "the label of target node cannot be null")

    @property
    def port_source(self):
        return self.node_source.label + "-" + self.node_target.label

    @port_source.setter
    def port_source(self, value):
        pass

    @property
    def port_target(self):
        return self.node_target.label + "-" + self.node_source.label

    @port_target.setter
    def port_target(self, value):
        pass

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
        self.__type = check_not_null(value = value, msg = "type of link cannot be null")


class DirectLinkOvsVeth(Link):
    def __init__(self, node_source = None, node_target = None):
        super().__init__(type = "direct-link-ovs-veth", node_source = node_source, node_target = node_target)

    def create(self):
        pid_src = self.node_source.node_pid
        pid_dst = self.node_target.node_pid
        if_src = self.port_source
        if_dst = self.port_target

        try:
            create_veth_link_containers(src_pid = pid_src, tgt_pid = pid_dst, src_ifname = if_src, tgt_ifname = if_dst)
            self.node_source.add_port(port = if_src)
            self.node_target.add_port(port = if_dst)
        except Exception as ex:
            print("Error: " + str(ex.args[0]))

    def delete(self):
        pid_src = self.node_source.node_pid
        pid_dst = self.node_target.node_pid
        if_src = self.port_source
        if_dst = self.port_target
        try:
            delete_veth_link_containers(src_pid = pid_src, tgt_pid = pid_dst, src_ifname = if_src, tgt_ifname = if_dst)
            self.node_source.del_port(port = if_src)
            self.node_source.del_port(port = if_dst)
        except Exception as ex:
            print("Error: " + ex.args[0])


class HostLinkOvsVeth(Link):
    def __init__(self, node_source = None, node_target = None, ip = None, gateway = None):
        super().__init__(type = "host-link-ovs-veth", node_source = node_source, node_target = node_target)
        self._ip = ip
        self._gateway = gateway

    def create(self):
        pid_src = self.node_source.node_pid
        pid_dst = self.node_target.node_pid
        if_src = self.port_source
        if_dst = self.port_target

        try:
            create_veth_link_containers(src_pid = pid_src, tgt_pid = pid_dst, src_ifname = if_src, tgt_ifname = if_dst)
            config_interface_address(pid = pid_src, if_name = if_src, addr = self._ip, gateway = self._gateway)
            self.node_target.add_port(port = if_dst)
        except Exception as ex:
            print("Error: " + ex.args[0])

    def delete(self):
        pid_src = self.node_source.node_pid
        pid_dst = self.node_target.node_pid
        if_src = self.port_source
        if_dst = self.port_target
        try:

            delete_veth_link_containers(src_pid = pid_src, tgt_pid = pid_dst, src_ifname = if_src, tgt_ifname = if_dst)
            self.node_target.del_port(port = if_dst)
        except Exception as ex:
            print("Error: " + ex.args[0])


class LinkGroup(object):
    def __init__(self):
        self.__links = {}

    def add_link(self, link):
        label = link.id
        self.__links.update({label: link})

    def rem_link(self, link):
        link.delete()
        del self.__links[link.id]

    def get_links(self):
        return self.__links.copy()

    def get_link(self, id):
        return self.__links[id]

    def commit(self):
        if len(self.__links) <= 0:
            raise RuntimeError("there is not link to commit")
        else:
            for k, v in self.__links.items():
                print("creating link {key} from {a} to {b}".format(key= k, a = v.port_source, b= v.port_target))
                v.create()

    def remove(self):
        if len(self.__links) <= 0:
            raise RuntimeError("there is not node to commit")
        else:
            for k, v in self.__links.items():
                print("removing link ({label})".format(label = k), )
                v.delete()
