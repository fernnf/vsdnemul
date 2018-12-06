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

import ipaddress
import random
from pathlib import Path
import os
import names
import shutil

from vsdnemul.lib import dockerlib as docker


def check_not_null(value, msg):
    if value is None:
        raise TypeError(msg)
    else:
        return value


def add_namespace_dir():
    dir = Path("/var/run/netns")
    if not dir.exists():
        dir.mkdir()
    else:
        raise FileExistsError("the namespace directory already exists")


def rem_namespace_dir():
    dir = Path("/var/run/netns")

    if dir.exists():
        shutil.rmtree(dir.as_posix())
    else:
        raise FileNotFoundError("the namespace directory not found")


def create_namespace(name: str, pid: int):
    dst = Path("/var/run/netns")
    src = Path("/proc/{pid}/ns/net".format(pid=pid))
    tgt = Path("/var/run/netns/{name}".format(name=name))

    if not dst.exists():
        raise FileNotFoundError("directory /var/run/netns not found")

    if not src.exists():
        raise FileNotFoundError("directory /proc/{pid}/ns/net not found".format(pid=pid))

    if not tgt.exists():
        tgt.symlink_to(src.as_posix())
    else:
        raise FileExistsError("the namespace already exists")


def delete_namespace(name: str):
    tgt = Path("/var/run/netns/{name}".format(name=name))

    if tgt.exists():
        tgt.unlink()
    else:
        raise FileNotFoundError("the symlink /var/run/netns/{name} not found".format(name=name))


def clean_namespaces():
    delete_namespace("*")


def is_valid_ip(addr: str):
    try:
        ipaddress.ip_address(address=addr)
        return True
    except:
        return False


def equals_ignore_case(a: str, b: str):
    return a.upper() == b.upper()


def rand_name():
    return names.get_first_name().lower()


def rand_interface_name():
    digits = 8
    lower = 10 ** (digits - 1)
    upper = 10 ** digits - 1

    return str(random.randint(lower, upper))


def disable_rx_off(netns, port_name):
    ethtool = Path("/usr/sbin/ethtool")
    if ethtool.exists():
        cmd = "{app} --offload {intf} rx off tx off".format(app=ethtool, intf=port_name)
        docker.run_cmd(name=netns, cmd=cmd)
    else:
        raise RuntimeError("the ethtool was not found")
