from cmd2 import Cmd, make_option, options

from vsdnemul.dataplane import Dataplane
from vsdnemul.node import Node
from vsdnemul.lib import equals_ignore_case
from vsdnemul.models.link import DirectLinkBridge, HostLinkBridge
from vsdnemul.models.link import DirectLinkOvs, HostLinkOvs
from vsdnemul.models.link import DirectLinkVeth, HostLinkVeth
from vsdnemul.models.node.host.host_node import Host
from vsdnemul.models.node.switch.whitebox_node import WhiteBox


class Prompt(Cmd):

    def __init__(self, dataplane: Dataplane):

        self.prompt = "[cli@vsdnemul]# "
        self.dataplane = dataplane

        Cmd.__init__(self, use_ipython = False)

    @options([
        make_option('-n', '--name', action = "store", type = "string", help = "the label of node to print information")
    ])
    def do_list_nodes(self, arg, opts):
        """ List information about all nodes or a specific node"""
        output = "\n Label: {label} " \
                 "\n Type: {type} " \
                 "\n Model: {model} " \
                 "\n Status: {status} " \
                 "\n Sevices: {services} " \
                 "\n Pid: {pid} \n"

        def print_node(node: Node):
            print("[{i}]".format(i = node.name))
            print(output.format(label = node.name,
                                type = node.type,
                                model = node.image,
                                status = node.node_status,
                                services = str(node.services),
                                pid = node.node_pid))
            print("[>]")

        def list_node(name):
            n = self.dataplane.get_node(name = name)
            print_node(node = n)

        def list_nodes():
            n = self.dataplane.get_nodes()
            if len(n) > 0:
                for k, v in n.items():
                    print_node(v)
            else:
                print("There is not nodes on topology")

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
        """Create a new node on topology. \nNodes types available:
        \n   1 - Whitebox \n   2 - Host
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

        else:
            print("the type node is unknown")

    @options([
        make_option("-n", "--name", action = "store", type = "string", help = "the label used by node")
    ])
    def do_delete_node(self, arg, opts):
        """Remove a node of topology"""

        exist = self.dataplane.exist_node(opts.name)

        if exist:
            node = self.dataplane.get_node(opts.name)
            node.delete()
            self.dataplane.del_node(name = opts.name)
            print("the node {name} has removed".format(name = opts.name))
        else:
            print("the node was not found")

    @options([
        make_option("-s", "--source", action = "store", type = "string", help = "the node ingress link"),
        make_option("-d", "--destination", action = "store", type = "string", help = "the node egress link"),
        make_option("-t", "--type", action = "store", type = "string",
                    help = "the type of technology that will be used by link"),
        make_option("-m", "--mtu", action = "store", type = "string", default = "1500",
                    help = "the mtu unit of link [default: %default]"),

    ])
    def do_create_direct_link(self, arg, opts):
        """Create a link between two nodes
        \ntechologies types:
        \n  1 - DirectLinkOvs \n  2 - DirectLinkBridge \n 3 - DirectVethLink
        """
        error = "Error: {msg}"
        success = "The {tech} link ({id}) has created"
        source = None
        target = None

        try:
            source = self.dataplane.get_node(opts.source)
            target = self.dataplane.get_node(opts.destination)
            if source.type.value() == 2 and target.type.value() == 2:
                if equals_ignore_case(opts.type, "directlinkovs"):

                    link = DirectLinkOvs(node_source = source, node_target = target, mtu = opts.mtu)
                    link.create()
                    self.dataplane.add_link(link = link)
                    print(success.format(tech = "link-direct-ovs", id = link.idx))

                elif equals_ignore_case(opts.type, "directlinkbridge"):

                    link = DirectLinkBridge(node_source = source, node_target = target, mtu = opts.mtu)
                    link.create()
                    self.dataplane.add_link(link = link)
                    print(success.format(tech = "link-direct-bridge", id = link.idx))

                elif equals_ignore_case(opts.type, "directvethlink"):
                    link = DirectLinkVeth(node_source = source, node_target = target, mtu = opts.mtu)
                    link.create()
                    self.dataplane.add_link(link = link)
                    print(success.format(tech = "link-direct-veth-pair", id = link.idx))

                else:
                    print(error.format("the technology type is unknown"))

        except Exception as ex:
            print(error.format(ex.args[0]))

    @options([
        make_option("-s", "--source", action = "store", type = "string", help = ""),
        make_option("-d", "--destination", action = "store", type = "string", help = ""),
        make_option("-t", "--type", action = "store", type = "string",
                    help = "the type of technology that will be used by link"),

        make_option("-m", "--mtu", action = "store", type = "string", default = "1500",
                    help = "the mtu unit of link [default: %default]"),
        make_option("-a", "--address", action = "store", type = "string", help = ""),
        make_option("-g", "--gateway", action = "store", type = "string", help = "")
    ])
    def do_create_host_link(self, arg, opts):
        """Create a link between two nodes
        \ntechologies types:
        \n  1 - HostLinkOvs \n  2 - HostLinkBridge
        """

        error = "Error: {msg}"
        success = "The {tech} link ({id}) has created"

        try:
            source = self.dataplane.exist_node(opts.source)
            target = self.dataplane.exist_node(opts.destination)

            if source.type.value() == 1 and target.type.value() == 2:

                if equals_ignore_case(opts.type, "hostlinkovs"):

                    link = HostLinkOvs(node_host = source, node_target = target, mtu = opts.mtu,
                                       ip_host = opts.address, gateway_host = opts.gateway)
                    link.create()
                    self.dataplane.add_link(link = link)
                    print(success.format(tech = "link-host-direct-ovs", id = link.idx))

                elif equals_ignore_case(opts.type, "hostlinkbridge"):
                    link = HostLinkBridge(node_host = source, node_target = target, mtu = opts.mtu,
                                          ip_host = opts.address, gateway_host = opts.gateway)

                    link.create()
                    self.dataplane.add_link(link = link)
                    print(success.format(tech = "link-host-direct-bridge", id = link.idx))

                elif equals_ignore_case(opts.type, "hostlinkveth"):

                    link = HostLinkVeth(node_host = source, node_target = target, mtu = opts.mtu,
                                        ip_host = opts.address, gateway_host = opts.gateway)

                    link.create()
                    self.dataplane.add_link(link = link)
                    print(success.format(tech = "link-host-direct-veth-pair", id = link.idx))

                else:
                    print(error.format("the technology type is unknown"))

            else:
                print(error.format("the node of target or source was not valid"))

        except Exception as ex:
            print(ex.args[0])

    @options([
        make_option("-i", "--id", action = "store", type = "string", help = ""),
    ])
    def do_list_links(self, arg, opts):

        output = "\n ID: {id} " \
                 "\n Source node: {src_node} " \
                 "\n Target node: {tgt_node} " \
                 "\n Source port: {src_port} " \
                 "\n Target port: {tgt_port} \n"

        def print_link(link):
            print("[{i}]".format(i = link.name))

            print(output.format(id = link.name,
                                src_node = link.node_source.name,
                                tgt_node = link.node_target.name,
                                src_port = link.port_source.name,
                                tgt_port = link.port_target.name))
            print("[>]")

        def list_link():
            link = self.dataplane.get_link(name = opts.id)
            print_link(link = link)

        def list_links():
            l = self.dataplane.get_links()
            for k, v in l.items():
                print_link(link = v)

        if opts.id is not None:
            list_link()
        else:
            list_links()

    @options([
        make_option("-n", "--name", action = "store", type = "string", help = "the label used by node"),
        make_option("-s", "--shell", action = "store", type = "string", default = "bash",
                    help = "the shell used by cli [default: %default]")
    ])
    def do_cli_node(self, arg, opts):
        """Get CLI terminal of node"""

        exist = self.dataplane.exist_node(opts.name)

        if exist:
            node = self.dataplane.get_node(opts.name)
            node.get_cli_prompt(shell = opts.shell)
        else:
            print("The node was not found on topology")

    @options([
        make_option("-i", "--id", action = "store", type = "string", help = "the link id on topology")
    ])
    def do_delete_link(self, arg, opts):

        if self.dataplane.exist_link(name = opts.id):
            link = self.dataplane.get_link(name = opts.id)
            link.delete()
            self.dataplane.del_link(name = opts.id)
            print("the link ({id}) has deleted".format(id = opts.id))
        else:
            print("the link was not found by id ({id})".format(id = opts.id))
