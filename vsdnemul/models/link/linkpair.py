import logging
from uuid import uuid4

from vsdnemul.lib import iproutelib as iproute
from vsdnemul.link import Link, LinkEncap, LinkType

MTU_DEFAULT = 9000

logger = logging.getLogger(__name__)


class LinkPair(Link):
