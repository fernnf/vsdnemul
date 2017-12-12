import os
import subprocess

import docker

from api.log.logapi import get_logger
from api.utils import check_not_null, create_namespace, delete_namespace

logger = get_logger("DockerApi")


def _create(name, image, ports = None, volumes = None, cap_app = None):
    check_not_null(name, "the name cannot be null")
    check_not_null(image, "the image name cannot be null")

    client = docker.from_env()
    client.containers.get()

    kwargs = dict()

    if ports is not None:
        kwargs.update(ports = ports)

    if volumes is not None:
        kwargs.update(volumes = volumes)

    if cap_app is not None:
        kwargs.update(cap_app = cap_app)

    kwargs.update(
        name = name,
        hostname = name,
        detach = True,
        tty = True,
        privileged = True,
        stdin_open = True,
        network_mode = "none"
    )

    container = client.containers.run(image = image, **kwargs)
    status = container.attrs["State"]["Status"]

    if status.__eq__("running"):
        pid = container.attrs["State"]["Pid"]
        create_namespace(pid = pid)
        return True
    else:
        return False


def _delete(name):
    check_not_null(name, "the container name cannot be null")
    client = docker.from_env()
    container = client.containers.get(container_id = name)
    pid = container.attrs["State"]["Pid"]
    delete_namespace(pid = pid)
    container.stop()
    container.remove()


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
    check_not_null(cmd, "the command cannot be null")
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

    terminal_cmd = "/usr/bin/xterm "
    docker_cmd = "/usr/bin/docker "
    if os.path.exists(terminal_cmd) and os.path.exists(docker_cmd):
        cmd = ["{cmd} -fg white -bg black -fa 'Liberation Mono' -fs 10 -e  {d_cmd} exec -it {node_name} {shell}"
                   .format(cmd = terminal_cmd, d_cmd = docker_cmd, node_name = name, shell = shell)]
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


class DockerApi(object):

    @staticmethod
    def get_id(name):
        try:
            return _id(name = name)
        except Exception as ex:
            logger.error(str(ex.args[1]))
            return None

    @staticmethod
    def create_node(name, image, ports = None, volumes = None, cap_app = None):
        try:
            return _create(name = name, image = image, ports = ports, volumes = volumes, cap_app = cap_app)
        except Exception as ex:
            logger.error(str(ex.args[1]))
            return None

    @staticmethod
    def delete_node(name):
        try:
            _delete(name = name)

        except Exception as ex:
            logger.error(str(ex.args[1]))

    @staticmethod
    def pause_node(name):
        try:
            _pause(name = name)
        except Exception as ex:
            logger.error(str(ex.args[1]))

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
            logger.error(str(ex.args[1]))
            return None

    @staticmethod
    def get_pid_node(name):
        try:
            return _pid(name = name)
        except Exception as ex:
            logger.error(str(ex.args[1]))
            return None

    @staticmethod
    def get_status_node(name):
        try:
            return _status(name = name)
        except Exception as ex:
            logger.error(str(ex.args[1]))
            return None

    @staticmethod
    def get_shell(name, shell = "bash"):
        try:
            _shell(name = name, shell = shell)
        except Exception as ex:
            logger.error(str(ex.args[1]))

    @staticmethod
    def rename_node(name, new_name):
        try:
            _rename(name = name, new_name = new_name)
        except Exception as ex:
            logger.error(str(ex.args[1]))

    @staticmethod
    def services_node(name):
        try:
            return _services(name = name)
        except Exception as ex:
            logger.error(str(ex.args[1]))
            return None

