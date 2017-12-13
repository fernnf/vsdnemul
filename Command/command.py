from cmd2 import Cmd, make_option, options
from Link.link import LinkGroup
from Link.vethlink import HostLinkOvsVeth, DirectLinkOvsVeth
from Node.node import NodeGroup, ApiNode
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

    @options([
        make_option("-l", "--label", action = "store", type = "string", help = "the label used by node")
    ])
    def do_delete_node(self, arg, opts):
        """Remove a node of topology

        """
        node = self.nodes.get_node(opts.label)

        if node is not None:
            node.delete()
            self.nodes.rem_node(node)
            print("the node has removed")
        else:
            print("the type node is unknown")

    @options([
        make_option("-s", "--source", action = "store", type= "string", help=""),
        make_option("-t", "--target", action = "store", type= "string", help=""),
    ])
    def do_create_direct_link(self, arg, opts):
        """Create a link between two nodes
        """
        source = self.nodes.get_node(opts.source)
        tartget = self.nodes.get_node(opts.target)

        if source is not None and tartget is not None:

            link = DirectLinkOvsVeth(node_source = source, node_target = tartget)
            link.create()

            self.links.add_link(link = link)
            print("the link has created")

        else:
            print("source or target node not found")

    @options([
        make_option("-s", "--host", action = "store", type = "string", help = ""),
        make_option("-t", "--target", action = "store", type = "string", help = ""),
    ])
    def do_create_host_link(self, arg, opts):

        source = self.nodes.get_node(opts.host)
        tartget = self.nodes.get_node(opts.target)

        if source is not None and tartget is not None:
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
        Source Node: {src_node}
        Target Node: {tgt_node}
        Source Port: {src_port}
        Target Port: {tgt_port}
        """

        def print_link(link):
            print("[{i}]".format(i = link.id))

            print(output.format(id = link.id,
                                src_node = link.node_source.label,
                                tgt_node = link.node_target.label,
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

        node = self.nodes.get_node(opts.label)
        if node is not None:
            node.get_cli_prompt()
        else:
            print("the node was not found")










