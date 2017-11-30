import os
import subprocess

import docker

from Api.utils import check_not_null, create_namespace


class DockerNodeApi(object):

    @staticmethod
    def create(name, image, ports = None, volumes = None, cap_app = None):

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

    @staticmethod
    def delete(name):
        check_not_null(name, "the container name cannot be null")
        client = docker.from_env()
        container = client.containers.get(container_id = name)
        container.stop()
        container.remove()

    @staticmethod
    def pause(name):
        check_not_null(name, "the container name cannot be null")
        client = docker.from_env()
        container = client.containers.get(container_id = name)
        container.pause()

    @staticmethod
    def resume(name):
        check_not_null(name, "the container name cannot be null")
        client = docker.from_env()
        container = client.containers.get(container_id = name)
        container.unpause()

    @staticmethod
    def exec(name, cmd):
        check_not_null(name, "the container name cannot be null")
        check_not_null(cmd, "the command cannot be null")
        client = docker.from_env()
        container = client.containers.get(container_id = name)

        return container.exec_run(cmd = cmd, tty = True, privileged = True)

    @staticmethod
    def pid(name):
        check_not_null(name, "the container name cannot be null")
        client = docker.from_env()
        container = client.containers.get(container_id = name)
        return container.attrs["State"]["Pid"]

    @staticmethod
    def status(name):
        check_not_null(name, "the container name cannot be null")
        client = docker.from_env()
        container = client.containers.get(container_id = name)
        return container.attrs["State"]["Pid"]

    @staticmethod
    def id(name):
        check_not_null(name, "the container name cannot be null")
        client = docker.from_env()
        container = client.containers.get(container_id = name)
        container.rename()
        return container.short_id

    @staticmethod
    def shell(name, shell = "bash"):
        check_not_null(name, "the container name cannot be null")

        terminal_cmd = "/usr/bin/xterm"
        docker_cmd = "/usr/bin/docker"
        if os.path.exists(terminal_cmd) and os.path.exists(docker_cmd):
            cmd = [terminal_cmd, "-fg", "white", "-bg", "black", "-e", docker_cmd, "exec", "-it", name, shell]
            subprocess.Popen(cmd)
        else:
            raise ValueError("xterm or docker not found")


class DockerNode(object):

    def __init__(self, name, image, ports = None, volumes = None, cap_app = None):

        self.name = name
        self.image = image
        self.ports = ports
        self.volumes = volumes
        self.cap_app = cap_app

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        if self.__name is not None:
            if self.__name != value:
                client = docker.from_env()
                container = client.containers.get(container_id = self.__name)
                container.rename(value)
                self.__name = value
        else:
            self.__name = value

    @property
    def image(self):
        return self.__image

    @image.setter
    def image(self, value):
        if self.__image is None:
            self.__image = value
        else:
            pass

    @property
    def ports(self):
        return self.__ports

    @ports.setter
    def ports(self, value):
        if self.__ports is None:
            self.__ports = value
        else:
            pass

    @property
    def volumes(self):
        return self.__volumes

    @volumes.setter
    def volumes(self, value):
        if self.__volumes is None:
            self.__volumes = value
        else:
            pass

    @property
    def cap_app(self):
        return self.__cap_app

    @cap_app.setter
    def cap_app(self, value):
        if self.__cap_app is None:
            self.__cap_app = value
        else:
            pass

    def id(self):
        try:
            if DockerNodeApi.status(name = self.name) == "running":
                return DockerNodeApi.id(name = self.name)
        except Exception as ex:
            return None

    def add(self):
        try:
            return DockerNodeApi.create(name = self.name, image = self.image, ports = self.ports,
                                        volumes = self.volumes, cap_app = self.cap_app)
        except Exception as ex:
            return False

    def delete(self):
        try:
            if DockerNodeApi.status(name = self.name) == "runnig":
                DockerNodeApi.delete(name = self.name)
            return True
        except Exception as ex:
            return False

    def shell(self, shell = "bash"):
        try:
            DockerNodeApi.shell(name = self.name, shell = shell)
        except Exception as ex:
            pass

    def status(self):
        try:
            return DockerNodeApi.status(name = self.name)
        except Exception as ex:
            return None

    def pid(self):
        try:
            if DockerNodeApi.status(name = self.name) == "running":
                return DockerNodeApi.pid(name = self.name)
        except Exception as ex:
            return None

    def pause(self):
        try:
            if DockerNodeApi.status(name = self.name) == "running":
                DockerNodeApi.pause(name = self.name)
        except Exception as ex:
            pass

    def unpause(self):
        try:
            if DockerNodeApi.status(name = self.name) == "paused":
                DockerNodeApi.resume(name = self.name)
        except Exception as ex:
            pass

    def exec(self, cmd):
        try:
            if DockerNodeApi.status(name = self.name) == "running":
                return DockerNodeApi.exec(name = self.name, cmd = cmd)
        except Exception as ex:
            pass
