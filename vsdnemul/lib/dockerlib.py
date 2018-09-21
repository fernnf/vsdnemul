import subprocess
from pathlib import Path

import docker

from vsdnemul.lib.utils import check_not_null, create_namespace, delete_namespace


def __create(image, **params):
    client = docker.from_env()

    params.update(
        detach=True,
        tty=True,
        privileged=True,
        stdin_open=True,
        init=True,
        environment=["container=docker"],
        ipc_mode="shareable",
        security_opt=["label=disable"]
    )

    client.containers.run(image=image, **params)
    container = client.containers.get(container_id=params.get("name"))
    status = container.attrs["State"]["Status"]

    if status.__eq__("running"):
        pid = container.attrs["State"]["Pid"]
        create_namespace(name=params.get("name"), pid=pid)
        return True
    else:
        return False


def __delete(name):
    delete_namespace(name=name)
    client = docker.from_env()
    container = client.containers.get(container_id=name)
    container.stop()
    container.remove()


def __pause(name):
    client = docker.from_env()
    container = client.containers.get(container_id=name)
    container.pause()


def __resume(name):
    client = docker.from_env()
    container = client.containers.get(container_id=name)
    container.unpause()


def __exec(name, cmd):
    client = docker.from_env()
    container = client.containers.get(container_id=name)
    return container.exec_run(cmd=cmd, tty=True, privileged=True)


def __pid(name):
    client = docker.from_env()
    container = client.containers.get(container_id=name)
    return container.attrs["State"]["Pid"]


def __status(name):
    client = docker.from_env()
    container = client.containers.get(container_id=name)
    return container.attrs["State"]["Status"]


def __id(name):
    client = docker.from_env()
    container = client.containers.get(container_id=name)
    return container.short_id


def __shell(name, shell="bash"):
    terminal = Path("/usr/bin/xterm")
    docker = Path("/usr/bin/docker")
    if terminal.is_file():
        cmd = [
            "{cmd} -T {node_name} -fg white -bg black -fa 'Liberation Mono' -fs 10 -e {d_cmd} exec -it {node_name} {shell}"
                .format(cmd=terminal.as_posix(), d_cmd=docker.as_posix(), node_name=name, shell=shell)]
        subprocess.Popen(cmd, shell=True)
    else:
        raise ValueError("xterm is not  found")


def __rename(name, new_name):
    check_not_null(name, "the container name cannot be null")
    check_not_null(new_name, "the container new name cannot be null")

    client = docker.from_env()
    container = client.containers.get(container_id=name)
    container.rename(new_name)


def __services(name):
    check_not_null(name, "the container name cannot be null")
    client = docker.from_env()
    container = client.containers.get(container_id=name)
    return container.attrs["Config"]["ExposedPorts"]


def __control_ip(name):
    check_not_null(name, "the container name cannot be null")
    client = docker.from_env()
    container = client.containers.get(container_id=name)
    return container.attrs["NetworkSettings"]["IPAddress"]


def get_id(name):
    check_not_null(name, "the image name cannot be null")
    try:
        return __id(name=name)
    except Exception as ex:
        raise RuntimeError(ex.__cause__)


def create_node(name, image, **params):
    check_not_null(image, "the image value cannot be null")
    try:
        params.update(name=name, hostname=name)
        return __create(image=image, **params)
    except Exception as ex:
        raise RuntimeError(ex.__cause__)


def delete_node(name):
    check_not_null(name, "the image name cannot be null")
    try:
        __delete(name=name)
    except Exception as ex:
        raise RuntimeError(ex.__cause__)


def pause_node(name):
    check_not_null(name, "the image name cannot be null")
    try:
        __pause(name=name)
    except Exception as ex:
        raise RuntimeError(ex.__cause__)


def run_cmd(name, cmd):
    check_not_null(name, "the image name cannot be null")
    try:
        return __exec(name=name, cmd=cmd)
    except Exception as ex:
        raise RuntimeError(ex.__cause__)


def resume_node(name):
    check_not_null(name, "the image name cannot be null")

    try:
        __resume(name=name)
    except Exception as ex:
        raise RuntimeError(ex.__cause__)


def get_pid_node(name):
    check_not_null(name, "the image name cannot be null")
    try:
        return __pid(name=name)
    except Exception as ex:
        raise RuntimeError(ex.__cause__)


def get_status_node(name):
    check_not_null(name, "the image name cannot be null")
    try:
        return __status(name=name)
    except Exception as ex:
        raise RuntimeError(ex.__cause__)


def get_shell(name, shell="bash"):
    check_not_null(name, "the image name cannot be null")
    try:
        __shell(name=name, shell=shell)
    except Exception as ex:
        raise RuntimeError(ex.__cause__)


def rename_node(name, new_name):
    check_not_null(name, "the image name cannot be null")
    check_not_null(new_name, "the new image name cannot be null")

    try:
        __rename(name=name, new_name=new_name)
    except Exception as ex:
        raise RuntimeError(ex.__cause__)


def services_node(name):
    check_not_null(name, "the image name cannot be null")

    try:
        return __services(name=name)
    except Exception as ex:
        raise RuntimeError(ex.__cause__)


def get_control_ip(name):
    check_not_null(name, "the image name cannot be null")

    try:
        return __control_ip(name=name)
    except Exception as ex:
        raise RuntimeError(ex.__cause__)
