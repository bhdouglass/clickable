from clickable import ProjectConfig
from clickable.commands.docker.docker_config import DockerConfig
from .docker_support import DockerSupport


class DebugValgrindSupport(DockerSupport):
    config = None

    def __init__(self, config: ProjectConfig):
        self.config = config

    def update(self, docker_config: DockerConfig):
        if self.config.debug_valgrind:
            docker_config.execute = 'valgrind {}'.format(docker_config.execute)
