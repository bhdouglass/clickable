from abc import ABC, abstractmethod

from clickable.commands.docker.docker_config import DockerConfig


class DockerSupport(ABC):
    @abstractmethod
    def update(self, docker_config: DockerConfig):
        pass
