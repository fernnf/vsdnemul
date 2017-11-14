from cmd2 import Cmd, make_option, options
from Link.link import LinkGroup
from Node.node import NodeGroup
from Node.whitebox import WhiteBox
from Node.host import Host
from utils import equals_ignore_case


class Prompt(Cmd):

    def __init__(self, links: LinkGroup, nodes: NodeGroup):

        self.prompt = "[vsdnagent]# "
        self.links = links
        self.nodes = nodes

        Cmd.__init__(self, use_ipython = False)

    @options([
        make_option('-l', '--label', action="store", type="string", help = "the label of node to print information")
    ])
    def do_list_nodes(self, arg, opts):
        """ List information about all nodes or a specific node"""
        output = """
        Label: {label}
        Type: {type} 
        Model: {model}
        Status: {status}
        Ip_Mgt: {ip_mgt}
        Sevices: {services}
        Pid: {pid}
        """

        def print_node(node):
            print("[{i}]".format(i = node.label))
            print(output.format(label = node.label,
                                type = node.node_type,
                                model = node.image,
                                status = node.node_status,
                                ip_mgt = node.control_ip,
                                services = str(node.service_exposed_port),
                                pid = node.node_pid))
            print(">")

        def list_node(label):
            n = self.nodes.get_node(label = label)
            print_node(node = n)

        def list_nodes():
            n = self.nodes.get_nodes()
            for k, v in n.items():
                print_node(v)

        if opts.label is None:
            list_nodes()
        else:
            list_node(opts.label)

    def do_quit(self, arg):
        print("Cleaning up topology")
        for k,v in self.nodes.get_nodes().items():
            v.delete()

        print("Quitting")
        return True

    @options([
        make_option("-l", "--label", action = "store", type = "string", help = "the label used by node"),
        make_option("-t", "--type", action = "store", type = "string", help = "the type of node eg: whitebox or host")
    ])
    def do_create_node(self, arg, opts):
        """
        Create a new node on topology.
        Nodes Available:
        1 - Whitebox
        2 - Host
        """
        if equals_ignore_case(opts.type, "whitebox"):
            node = WhiteBox(label = opts.label)
            node.create()
            self.nodes.add_node(node = node)
            print("the whitebox node ({label}) has created".format(label = node.label))

        elif equals_ignore_case(opts.type, "host"):
            node = Host(label = opts.label)
            node.create()
            self.nodes.add_node(node = node)
            print("the host node ({label}) has created".format(label = node.label))

        else:
            print("the type node is unknown")


