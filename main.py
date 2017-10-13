import argparse
import json
from node import WhiteBox, NodeCommand
from link import LinkSwitch, LinkCommand

from functions import ApiNode


if __name__ == '__main__':

    name = "host1"
    image = "fedora/systemd-systemd"
    service = {'22/tcp': None}

    ApiNode.nodeCreate(name = name, type = image, service = service)
