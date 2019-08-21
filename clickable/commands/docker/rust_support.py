import os

from clickable.commands.docker.docker_config import DockerConfig
from clickable.config import Config
from .docker_support import DockerSupport


class RustSupport(DockerSupport):
    config = None

    def __init__(self, config: Config):
        self.config = config

    def update(self, docker_config: DockerConfig):
        template = self.config.config['template']

        if template == Config.RUST:
            cargo_home = self.config.cargo_home
            cargo_registry = os.path.join(cargo_home, 'registry')
            cargo_git = os.path.join(cargo_home, 'git')

            os.makedirs(cargo_registry, exist_ok=True)
            os.makedirs(cargo_git, exist_ok=True)

            docker_config.add_volume_mappings({
                cargo_registry: '/opt/rust/cargo/registry',
                cargo_git: '/opt/rust/cargo/git'
            })
