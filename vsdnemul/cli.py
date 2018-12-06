#  Copyright @2018
#
#  GERCOM - Federal University of Pará - Brazil
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import cmd2
from cmd2 import with_category

from vsdnemul.link import CliLink
from vsdnemul.node import CliNode

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

