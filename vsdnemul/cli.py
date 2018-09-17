import argparse

import cmd2
from cmd2 import with_argparser, with_category
from terminaltables import AsciiTable
from vsdnemul.node import CliNode
from vsdnemul.link import CliLink

CMD_CAT_MANAGER_NODE = "Manager Resources Emulation"


class Cli(cmd2.Cmd):


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

    @with_category(CMD_CAT_MANAGER_NODE)
    def do_link(self, args):
        """List all information of the Nodes or Links"""
        i = CliLink(dataplane=self.__dp)
        i.prompt = self.prompt[:-7] + 'Link]# '
        i.cmdloop()


if __name__ == '__main__':
    cli = Cli()
    cli.cmdloop()
