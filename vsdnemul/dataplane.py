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

import logging
import traceback
from vsdnemul.link import LinkFabric
from vsdnemul.node import NodeFabric
from vsdnemul.lib import utils

logger = logging.getLogger(__name__)

def _AddNamespceDir():
    try:
        utils.add_namespace_dir()
    except Exception as ex:
        logger.warning(ex.args[0])

def _RemNamespaceDir():
    try:
        utils.rem_namespace_dir()
    except Exception as ex:
        traceback.print_exc()
        logger.warning(ex.args[0])

class Dataplane(object):

    def __init__(self):
        self.__nodes = NodeFabric()
        self.__links = LinkFabric()

        _AddNamespceDir()

    def addNode(self, node):
        try:
            return self.__nodes.addNode(node=node)
        except Exception as ex:
            logger.error(ex.args[0])

    def delNode(self, name):
        try:
            self.__nodes.delNode(name)
        except Exception as ex:
            logger.error(ex.args[0])

    def addLink(self, link):
        try:
            return self.__links.addLink(link)
        except Exception as ex:
            logger.error(ex.args[0])

    def delLink(self, name):

        try:
            self.__links.delLink(name)
        except Exception as ex:
            logger.error(ex.args[0])

    def getNode(self, name):
        return self.__nodes.getNode(name)

    def getNodeId(self, name):
        for n in self.__nodes.getNodes().values():
            if n.getName().__eq__(name):
                return n.getId()
        return self.__nodes.getNode(name).getId()

    def getLink(self, name):
        return self.__links.getLink(name)

    def getNodes(self):
        return self.__nodes.getNodes()

    def getLinks(self):
        return self.__links.getLinks()

    def getCountNodes(self):
        return self.__nodes.getNodes().__len__()

    def getCountLinks(self):
        return self.__links.getLinks().__len__()


    def stop(self):
        def destroyLinks():
            for key,link in self.__links.getLinks().items():
                logger.info("Deleting link ({key}:{name})".format(name=link.getName(), key=link.getId()))
                link._Destroy()

        def destroyNodes():
            for key,node in self.__nodes.getNodes().items():
                logger.info("Deleting node ({key}:{name}) ".format(name=node.getName(), key=node.getId()))
                node._Destroy()
        try:
            if self.getCountLinks() > 0:
                destroyLinks()
            else:
                logger.warning("no links to destroy")

            if self.getCountNodes() > 0:
                destroyNodes()
            else:
                logger.warning("no links to destroy")
        except Exception as ex:
            logger.error(ex.args)
