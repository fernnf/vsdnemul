import argparse

import cmd2
from cmd2 import with_argparser, with_category
from terminaltables import AsciiTable


class CliNode(cmd2.Cmd):
    CAT_NODE_MANAGER = "Node Emulation Command"

    def __init__(self, dataplane=None):
        super(CliNode, self).__init__()
        self.dp = dataplane

    list_parser = argparse.ArgumentParser()
    list_parser.add_argument('-a', '--all', action='store_true', dest="all", help='display all nodes from emulation')
    list_parser.add_argument('-i', '--id', action="store", dest="id",
                             help="retrieve all information from specific node")
    list_parser.set_defaults(all=False)
    list_parser.set_defaults(id=None)

    @with_category(CAT_NODE_MANAGER)
    @with_argparser(list_parser)
    def do_list(self, opts):
        """Manager node options of the emulation"""

        def print_data(node):
            data = []

            cid = ["ID", "{id}".format(id=node.getId())]
            data.append(cid)
            name = ["Name", "{name}".format(name=node.getName())]
            data.append(name)
            type = ["Type", "{type}".format(type=node.getType().describe())]
            data.append(type)
            ipmgt = ["Ip Control", "{ip}".format(ip=node.getControlIp())]
            data.append(ipmgt)
            status = ["Status", "{status}".format(status=node.getStatus())]
            data.append(status)

            tables = AsciiTable(data, title="Node: {name}".format(name=node.getName()))
            tables.justify_columns[2] = 'right'

            self.poutput(msg=tables.table)
            self.poutput(msg="")

        def list_all():
            nodes = self.dp.getNodes()

            for n in nodes.values():
                print_data(node=n)

        if opts.id is not None:
            try:
                node = self.dp.getNode(opts.id)
                print_data(node=node)
            except:
                self.perror("the node not exists")
        elif opts.all:
            list_all()
        else:
            self.perror("option unknown")

    def do_quit(self, arg):
        "Exits the emulator"
        print("Quitting")
        raise SystemExit

    def do_exit(self, s):
        return True


class Cli(cmd2.Cmd):
    CMD_CAT_MANAGER_NODE = "Manager Resources Emulation"

    def __init__(self, dataplane=None):
        super().__init__(use_ipython=False)
        self.__dp = dataplane
        self.prompt = "[vsdnemul@Root]# "

    def do_exit(self, args):
        return True

    @with_category(CMD_CAT_MANAGER_NODE)
    def do_node(self, args):
        """List all information of the Nodes or Links"""
        i = CliNode(dataplane=self.__dp)
        i.prompt = self.prompt[:-7] + 'Node]# '
        i.cmdloop()


if __name__ == '__main__':
    cli = Cli()
    cli.cmdloop()
