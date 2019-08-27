from clickable.commands.docker.docker_config import DockerConfig
from clickable.commands.docker.docker_support import DockerSupport
from clickable.system.require import Require
from clickable.system.requirements.nvidia_container_toolkit import NvidiaContainerToolkit


class NvidiaSupportSinceDockerVersion1903(DockerSupport):
    def update(self, docker_config: DockerConfig):
        self.validate_system_requirements_are_met()
        docker_config.add_extra_options({
            '--gpus': 'all',
        })

    def validate_system_requirements_are_met(self):
        Require(NvidiaContainerToolkit()).or_exit()
