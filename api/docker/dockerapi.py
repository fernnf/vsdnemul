import subprocess
from pathlib import Path

import docker

from api.log.logapi import get_logger
from api.utils.utils import check_not_null, create_namespace, delete_namespace

logger = get_logger(__name__)


def _create(name, image, ports = None, volumes = None, cap_add = None):
    check_not_null(name, "the name cannot be null")
    check_not_null(image, "the image name cannot be null")

    client = docker.from_env()

    kwargs = dict()

    if ports is not None:
        kwargs.update(ports = ports)

    if volumes is not None:
        kwargs.update(volumes = volumes)

    if cap_add is not None:
        kwargs.update(cap_add = cap_add)

    kwargs.update(
        name = name,
        hostname = name,
        detach = True,
        tty = True,
        privileged = True,
        stdin_open = True,
        init = True,
        environment = ["container=docker"],
        ipc_mode = "shareable",
        security_opt = ["label=disable"]
    )

    client.containers.run(image = image, **kwargs)
    container = client.containers.get(container_id = name)
    status = container.attrs["State"]["Status"]

    if status.__eq__("running"):
        pid = container.attrs["State"]["Pid"]
        create_namespace(name = name, pid = pid)
        return True
    else:
        return False


def _delete(name):
    check_not_null(name, "the container name cannot be null")
    client = docker.from_env()
    container = client.containers.get(container_id = name)
    container.stop()
    container.remove()
    delete_namespace(name = name)


def _pause(name):
    check_not_null(name, "the container name cannot be null")
    client = docker.from_env()
    container = client.containers.get(container_id = name)
    container.pause()


def _resume(name):
    check_not_null(name, "the container name cannot be null")
    client = docker.from_env()
    container = client.containers.get(container_id = name)
    container.unpause()


def _exec(name, cmd):
    check_not_null(name, "the container name cannot be null")
    check_not_null(cmd, "the frontend cannot be null")
    client = docker.from_env()
    container = client.containers.get(container_id = name)
    return container.exec_run(cmd = cmd, tty = True, privileged = True)


def _pid(name):
    check_not_null(name, "the container name cannot be null")
    client = docker.from_env()
    container = client.containers.get(container_id = name)
    return container.attrs["State"]["Pid"]


def _status(name):
    check_not_null(name, "the container name cannot be null")
    client = docker.from_env()
    container = client.containers.get(container_id = name)
    return container.attrs["State"]["Status"]


def _id(name):
    check_not_null(name, "the container name cannot be null")
    client = docker.from_env()
    container = client.containers.get(container_id = name)
    return container.short_id


def _shell(name, shell = "bash"):
    check_not_null(name, "the container name cannot be null")

    terminal = Path("/usr/bin/xterm")
    docker = Path("/usr/bin/docker")
    if docker.is_file() and terminal.is_file():
        cmd = ["{cmd} -T {node_name} -fg white -bg black -fa 'Liberation Mono' -fs 10 -e {d_cmd} exec -it {node_name} {shell}"
                   .format(cmd = terminal.as_posix(), d_cmd = docker.as_posix(), node_name = name, shell = shell)]
        subprocess.Popen(cmd, shell = True)
    else:
        raise ValueError("xterm or docker not found")


def _rename(name, new_name):
    check_not_null(name, "the container name cannot be null")
    check_not_null(new_name, "the container new name cannot be null")

    client = docker.from_env()
    container = client.containers.get(container_id = name)
    container.rename(new_name)


def _services(name):
    check_not_null(name, "the container name cannot be null")
    client = docker.from_env()
    container = client.containers.get(container_id = name)
    return container.attrs["Config"]["ExposedPorts"]


def _control_ip(name):
    check_not_null(name, "the container name cannot be null")
    client = docker.from_env()
    container = client.containers.get(container_id = name)
    return container.attrs["NetworkSettings"]["IPAddress"]


class DockerApi(object):

    @staticmethod
    def get_id(name):
        try:
            return _id(name = name)
        except Exception as ex:
            logger.error(str(ex))
            return None

    @staticmethod
    def create_node(name, image, ports = None, volumes = None, cap_add = None):
        try:
            return _create(name = name, image = image, ports = ports, volumes = volumes, cap_add = cap_add)
        except Exception as ex:
            logger.error(str(ex))
            return None

    @staticmethod
    def delete_node(name):
        try:
            _delete(name = name)
            return True
        except Exception as ex:
            logger.error(str(ex))
            return False

    @staticmethod
    def pause_node(name):
        try:
            _pause(name = name)
        except Exception as ex:
            logger.error(str(ex.args))

    @staticmethod
    def resume_node(name):
        try:
            _resume(name = name)
        except Exception as ex:
            logger.error(str(ex.args[1]))

    @staticmethod
    def run_cmd(name, cmd):
        try:
            return _exec(name = name, cmd = cmd)
        except Exception as ex:
            logger.error(str(ex.args))
            return None

    @staticmethod
    def get_pid_node(name):
        try:
            return _pid(name = name)
        except Exception as ex:
            logger.error(str(ex.args))
            return None

    @staticmethod
    def get_status_node(name):
        try:
            return _status(name = name)
        except Exception as ex:
            logger.error(str(ex.args))
            return None

    @staticmethod
    def get_shell(name, shell = "bash"):
        try:
            _shell(name = name, shell = shell)
        except Exception as ex:
            logger.error(str(ex.args))

    @staticmethod
    def rename_node(name, new_name):
        try:
            _rename(name = name, new_name = new_name)
        except Exception as ex:
            logger.error(str(ex.args))

    @staticmethod
    def services_node(name):
        try:
            return _services(name = name)
        except Exception as ex:
            logger.error(str(ex.args))
            return None

    @staticmethod
    def get_control_ip(name):
        try:
            return _control_ip(name = name)
        except Exception as ex:
            logger.error(str(ex.args))
