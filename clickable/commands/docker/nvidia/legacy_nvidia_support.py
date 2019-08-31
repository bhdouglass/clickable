from clickable.commands.docker.docker_config import DockerConfig
from clickable.commands.docker.docker_support import DockerSupport
from clickable.system.require import Require
from clickable.system.requirements.nvidia_docker import NvidiaDocker
from clickable.system.requirements.nvidia_modprobe import NvidiaModprobe


class LegacyNvidiaSupport(DockerSupport):
    def update(self, docker_config: DockerConfig):
        self.validate_system_requirements_are_met()
        docker_config.docker_executable = 'nvidia-docker'

    def validate_system_requirements_are_met(self):
        Require(NvidiaModprobe()).or_exit()
        Require(NvidiaDocker()).or_exit()

