from clickable.commands.docker.docker_config import DockerConfig
from clickable.system.queries.legacy_docker_version import LegacyDockerVersion
from clickable.system.queries.nvidia_drivers_in_use import NvidiaDriversInUse
from .docker_support import DockerSupport
from .nvidia.legacy_nvidia_support import LegacyNvidiaSupport
from .nvidia.nvidia_support_since_docker_version_1903 import NvidiaSupportSinceDockerVersion1903


class NvidiaSupport(DockerSupport):
    def update(self, docker_config: DockerConfig):
        if docker_config.use_nvidia:
            docker_config.add_volume_mappings({
                '/dev/snd/pcmC2D0c': '/dev/snd/pcmC2D0c',
                '/dev/snd/controlC2': '/dev/snd/controlC2'
            })
            docker_config.add_extra_options({
                '--device': '/dev/snd',
            })

            if LegacyDockerVersion().is_met():
                LegacyNvidiaSupport().update(docker_config)
                return

            NvidiaSupportSinceDockerVersion1903().update(docker_config)
