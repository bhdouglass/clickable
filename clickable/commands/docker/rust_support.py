import os

from clickable.commands.docker.docker_config import DockerConfig
from clickable.config.project import ProjectConfig
from clickable.config.constants import Constants
from .docker_support import DockerSupport


class RustSupport(DockerSupport):
    config = None

    def __init__(self, config: ProjectConfig):
        self.config = config

    def update(self, docker_config: DockerConfig):
        builder = self.config.builder

        if builder == Constants.RUST:
            cargo_home = self.config.cargo_home
            cargo_registry = os.path.join(cargo_home, 'registry')
            cargo_git = os.path.join(cargo_home, 'git')

            os.makedirs(cargo_registry, exist_ok=True)
            os.makedirs(cargo_git, exist_ok=True)

            docker_config.add_volume_mappings({
                cargo_registry: '/opt/rust/cargo/registry',
                cargo_git: '/opt/rust/cargo/git'
            })
