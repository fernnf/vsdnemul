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

from ryu.lib.ovs import vsctl

logger = logging.getLogger(__name__)

LOCAL = "tcp:127.0.0.1:6640"


def set_ovsdb(db_addr=LOCAL, table=[], value=[]):
    ovsdb = vsctl.VSCtl(db_addr)
    command = "set"
    args = table + value
    run = vsctl.VSCtlCommand(command, args)
    try:
        ovsdb.run_command([run])
        return run.result
    except Exception as ex:
        raise RuntimeError(str(ex))


def get_ovsdb(db_addr=LOCAL, table=[], value=[]):
    ovsdb = vsctl.VSCtl(db_addr)
    command = "get"
    value = table + value
    run = vsctl.VSCtlCommand(command, value)
    try:
        ovsdb.run_command([run])
        return run.result
    except Exception as ex:
        raise RuntimeError(ex.args[0])


def exists_bridge(name, db_addr=LOCAL):
    ovsdb = vsctl.VSCtl(db_addr)
    command = "br-exists"
    args = [name]
    run = vsctl.VSCtlCommand(command, args)
    try:
        ovsdb.run_command([run])
        return run.result
    except Exception as ex:
        raise RuntimeError(ex.args[0])


def add_bridge(name, db_addr=LOCAL, protocols=None, datapath_id=None):
    ovsdb = vsctl.VSCtl(db_addr)

    def create():
        command = "add-br"
        args = [name]
        run = vsctl.VSCtlCommand(command, args)
        ovsdb.run_command([run])
        return run.result

    def set_ofversion():
        table = ["Bridge"]
        value = [name, "protocols={version}".format(version=protocols)]
        set_ovsdb(db_addr=db_addr, table=table, value=value)

    def set_dpid():
        table = ["Bridge"]
        value = [name, "other_config:datapath-id={dpid}".format(dpid=datapath_id)]
        set_ovsdb(db_addr=db_addr, table=table, value=value)

    try:
        if not exists_bridge(name=name, db_addr=db_addr):
            create()
        if protocols is not None:
            set_ofversion()
        if datapath_id is not None:
            set_dpid()
    except Exception as ex:
        raise RuntimeError(str(ex) + " " + datapath_id)


def rem_bridge(name, db_addr=LOCAL):
    ovsdb = vsctl.VSCtl(db_addr)
    command = "del-br"
    args = [name]
    run = vsctl.VSCtlCommand(command, args)
    try:
        if exists_bridge(db_addr, name):
            ovsdb.run_command([run])
    except Exception as ex:
        raise RuntimeError(ex.args[0])


def set_bridge_controller(name, target_addr, db_addr=LOCAL):
    ovsdb = vsctl.VSCtl(db_addr)
    command = "set-controller"
    args = [name, target_addr]
    run = vsctl.VSCtlCommand(command, args)
    try:
        if exists_bridge(name=name, db_addr=db_addr):
            ovsdb.run_command([run])
    except Exception as ex:
        raise RuntimeError(ex.args[0])


def del_bridge_controller(name, db_addr=LOCAL):
    ovsdb = vsctl.VSCtl(db_addr)
    command = "del-controller"
    args = [name]
    run = vsctl.VSCtlCommand(command, args)
    try:
        if exists_bridge(name=name, db_addr=db_addr):
            ovsdb.run_command([run])
    except Exception as ex:
        raise RuntimeError(ex.args[0])


def add_port_bridge(db_addr, name, port_name, patch=False, peer=None, ofport=None):
    ovsdb = vsctl.VSCtl(db_addr)

    def adding():
        command = "add-port"
        args = [name, port_name]
        run = vsctl.VSCtlCommand(command, args)
        ovsdb.run_command([run])

    def set_ofport():
        table = ["Interface"]
        value = [port_name, "ofport_request={ofport}".format(ofport=ofport)]
        set_ovsdb(db_addr, table, value)

    def set_patch():
        table = ["Interface"]
        value = [port_name, "type=patch"]
        set_ovsdb(db_addr, table, value)

    def set_peer():
        table = ["Interface"]
        value = [port_name, "options:peer={}".format(peer)]
        set_ovsdb(db_addr, table, value)

    try:
        adding()
        if ofport is not None:
            set_ofport()
        if patch:
            set_patch()
            if peer is None:
                raise ValueError("patch must have peer port")
            set_peer()
    except Exception as ex:
        raise RuntimeError(ex.args[0])


def del_port_bridge(db_addr, name, port_name):
    ovsdb = vsctl.VSCtl(db_addr)
    command = "del-port"
    args = [name, port_name]
    run = vsctl.VSCtlCommand(command, args)

    try:
        ovsdb.run_command([run])
    except Exception as ex:
        raise RuntimeError(ex.args[0])
