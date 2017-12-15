from cmd2 import Cmd, make_option, options

from api.dataplane.dataplaneapi import Dataplane
from api.node.nodeapi import Node
from api.utils import equals_ignore_case
from link.bridge_link import DirectLinkBridge, HostLinkBridge
from link.ovs_link import DirectLinkOvs, HostLinkOvs
from node.host_node import Host
from node.whitebox_node import WhiteBox


class Prompt(Cmd):

    def __init__(self, dataplane: Dataplane):

        self.prompt = "[cli@vsdnagent]# "
        self.dataplane = dataplane

        Cmd.__init__(self, use_ipython = False)

    @options([
        make_option('-n', '--name', action = "store", type = "string", help = "the label of node to print information")
    ])
    def do_list_nodes(self, arg, opts):
        """ List information about all nodes or a specific node"""
        output = """
        Label: {label}
        Type: {type} 
        Model: {model}
        Status: {status}
        Sevices: {services}
        Pid: {pid}
        """

        def print_node(node: Node):
            print("[{i}]".format(i = node.name))
            print(output.format(label = node.name,
                                type = node.type,
                                model = node.image,
                                status = node.node_status,
                                services = str(node.service_exposed),
                                pid = node.node_pid))
            print("[>]")

        def list_node(name):
            n = self.dataplane.get_node(name = name)
            print_node(node = n)

        def list_nodes():
            n = self.dataplane.get_nodes()
            for k, v in n.items():
                print_node(v)

        if opts.name is None:
            list_nodes()
        else:
            list_node(opts.name)

    def do_quit(self, arg):
        print("Cleaning up topology")
        self.dataplane.delete()
        print("Quitting")
        return True

    @options([
        make_option("-n", "--name", action = "store", type = "string", help = "the label used by node"),
        make_option("-t", "--type", action = "store", type = "string", help = "the type of node eg: whitebox or host")
    ])
    def do_create_node(self, arg, opts):
        """
        Create a new node on topology.
        Nodes Available:
        1 - Whitebox
        2 - Host
        3 - ONOS
        """
        if equals_ignore_case(opts.type, "whitebox"):
            node = WhiteBox(name = opts.name)
            node.create()
            self.dataplane.add_node(node = node)
            print("the whitebox node ({name}) has created".format(name = node.name))

        elif equals_ignore_case(opts.type, "host"):
            node = Host(name = opts.name)
            node.create()
            self.dataplane.add_node(node = node)
            print("the host node ({name}) has created".format(name = node.name))

        elif equals_ignore_case(opts.type, "onos"):
            node = Host(name = opts.name)
            node.create()
            self.dataplane.add_node(node = node)
            print("the host node ({name}) has created".format(name = node.name))

        else:
            print("the type node is unknown")

    @options([
        make_option("-n", "--name", action = "store", type = "string", help = "the label used by node")
    ])
    def do_delete_node(self, arg, opts):
        """Remove a node of topology

        """
        node = self.dataplane.get_node(opts.name)

        if node is not None:
            node.delete()
            self.dataplane.del_node(name = opts.name)
            print("the node {name} has removed".format(name = opts.name))
            del node
        else:
            print("the type node is unknown")

    @options([
        make_option("-s", "--source", action = "store", type = "string", help = "the node ingress link"),
        make_option("-d", "--destination", action = "store", type = "string", help = "the node egress link"),
        make_option("-t", "--type", action = "store", type = "string",
                    help = "the type of technology that will be used by link"),

    ])
    def do_create_direct_link(self, opts):
        """Create a link between two nodes
        \ntechologies types:
        \n  1 - DirectLinkOvs \n  2 - HostLinkOvs \n  3 - DirectLinkBridge \n  4 - HostLinkBridge
        """
        error = "Error: {msg}"
        success = "The {tech} link ({id}) has created"

        source = self.dataplane.exist_node(opts.source)
        target = self.dataplane.exist_node(opts.destination)

        if source is True and target is True:
            if equals_ignore_case(opts.type, "directlinkovs"):
                node_src = self.dataplane.get_node(name = opts.source)
                node_tgt = self.dataplane.get_node(name = opts.destination)

                link = DirectLinkOvs(node_source = node_src, node_target = node_tgt, mtu = opts.mtu)
                link.create()
                self.dataplane.add_link(link = link)
                print(success.format(tech = "link-direct-ovs", id = link.id))

            elif equals_ignore_case(opts.type, "hostlinkovs"):
                host_src = self.dataplane.get_node(name = opts.source)
                node_tgt = self.dataplane.get_node(name = opts.destination)

                link = HostLinkOvs(node_host = host_src, node_target = node_tgt, mtu = opts.mtu, ip_host = opts.address,
                                   gateway_host = opts.gateway)
                link.create()
                self.dataplane.add_link(link = link)
                print(success.format(tech = "link-host-direct-ovs", id = link.id))

            elif equals_ignore_case(opts.type, "directlinkbridge"):
                node_src = self.dataplane.get_node(name = opts.source)
                node_tgt = self.dataplane.get_node(name = opts.destination)

                link = DirectLinkBridge(node_source = node_src, node_target = node_tgt)

                link.create()
                self.dataplane.add_link(link = link)
                print(success.format(tech = "link-direct-bridge", id = link.id))

            elif equals_ignore_case(opts.type, "hostlinkbridge"):
                host_src = self.dataplane.get_node(name = opts.source)
                node_tgt = self.dataplane.get_node(name = opts.destination)

                link = HostLinkBridge(node_source = host_src, node_target = node_tgt, mtu = opts.mtu,
                                      ip_host = opts.address, gateway_host = opts.gateway)

                link.create()
                self.dataplane.add_link(link = link)
                print(success.format(tech = "link-host-direct-bridge", id = link.id))

            else:
                print(error.format("the technology type is unknown"))
        else:
            print(error.format("the node of target or source was not found"))

    @options([
        make_option("-h", "--host", action = "store", type = "string", help = ""),
        make_option("-d", "--destination", action = "store", type = "string", help = ""),
        make_option("-t", "--type", action = "store", type = "string",
                    help = "the type of technology that will be used by link"),

        make_option("-m", "--mtu", action = "store", type = "string", default = "1500",
                    help = "the mtu unit of link [default: %default]"),
        make_option("-a", "--address", action = "store", type = "string", help = ""),
        make_option("-g", "--gateway", action = "store", type = "string", help = "")
    ])
    def do_create_host_link(self, arg, opts):

        error = "Error: {msg}"
        success = "The {tech} link ({id}) has created"

        source = self.dataplane.exist_node(opts.source)
        target = self.dataplane.exist_node(opts.destination)




        if source is True and tartget is True:
            link = HostLinkOvsVeth(node_host = opts.host, node_target = opts.target)
            link.create()
            self.links.add_link(link = link)
            print("the link has created")
        else:
            print("host or target node not found")

    @options([
        make_option("-i", "--id", action = "store", type = "string", help = ""),
    ])
    def do_list_links(self, arg, opts):

        output = """
        ID: {id}
        Source node: {src_node}
        Target node: {tgt_node}
        Source port: {src_port}
        Target port: {tgt_port}
        """

        def print_link(link):
            print("[{i}]".format(i = link.id))

            print(output.format(id = link.id,
                                src_node = link.node_source.name,
                                tgt_node = link.node_target.name,
                                src_port = link.port_source,
                                tgt_port = link.port_target))

        def list_link():
            link = self.links.get_link(opts.id)
            print_link(link = link)

        def list_links():
            l = self.links.get_links()
            for k, v in l.items():
                print_link(link = v)

        if opts.id is not None:
            list_link()
        else:
            list_links()

    @options(
        make_option("-l", "--label", action = "store", type = "string", help = "the label used by node")
    )
    def do_cli_node(self, arg, opts):

        node = self.nodes.get_node(opts.name)
        if node is not None:
            node.get_cli_prompt()
        else:
            print("the node was not found")
