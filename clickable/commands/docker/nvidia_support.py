from clickable.commands.docker.docker_config import DockerConfig
from .docker_support import DockerSupport


class NvidiaSupport(DockerSupport):
    def update(self, docker_config: DockerConfig):
        if (docker_config.use_nvidia):
            docker_config.add_volume_mappings({
                '/dev/snd/pcmC2D0c': '/dev/snd/pcmC2D0c',
                '/dev/snd/controlC2': '/dev/snd/controlC2'
            })
            docker_config.add_extra_options({
                '--runtime': 'nvidia',
                '--device': '/dev/snd',
            })
