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
        raise RuntimeError(ex.args[0])


def get_ovsdb(db_addr=LOCAL, table=[], args=[]):
    ovsdb = vsctl.VSCtl(db_addr)
    command = "get"
    args = table + args
    run = vsctl.VSCtlCommand(command, args)
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
        set_ovsdb(table, value)

    def set_dpid():
        table = ["Bridge"]
        value = [name, "other-config:datapath-id={dpid}".format(dpid=datapath_id)]
        set_ovsdb(table, value)

    try:
        if not exists_bridge(name=name, db_addr=db_addr):
            create()
        if protocols is not None:
            set_ofversion()
        if datapath_id is not None:
            set_dpid()
    except Exception as ex:
        raise RuntimeError(ex.args[0])


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


def set_bridge_controller(name, db_addr=LOCAL, target_addr=[]):
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


def add_port_bridge(db_addr, name, port_name, ofport=None):
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

    try:
        adding()
        if ofport is not None:
            set_ofport()
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
