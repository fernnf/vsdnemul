from vsdnemul.models.node.switch.whitebox import Whitebox
from vsdnemul.models.link.bridge import Bridge, LinkType
from vsdnemul.dataplane import Dataplane

from vsdnemul.lib.log import get_logger

def topology():

    dp = Dataplane()

    sw1 = dp.addNode(Whitebox(name="sw1"))
    print(sw1.getId())
    print(sw1.getControlAddr())
    sw2 = dp.addNode(Whitebox(name="sw2"))
    print(sw2.getId())
    print(sw2.getControlAddr())

    l1 = dp.addLink(Bridge(name="l1", node_source=sw1, node_target=sw2, type=LinkType.DIRECT))

    print(dp.getLinks())
    return dp


if __name__ == '__main__':

    logger = get_logger(__name__)
    dp = topology()

    dp.stop()

