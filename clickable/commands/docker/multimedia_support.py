from clickable import ProjectConfig
from clickable.commands.docker.docker_config import DockerConfig
from .docker_support import DockerSupport
import os
import getpass

class MultimediaSupport(DockerSupport):
    config = None

    def __init__(self, config: ProjectConfig):
        self.config = config

    def update(self, docker_config: DockerConfig):
        uid = os.getuid()
        user = getpass.getuser()
        
        docker_config.volumes.update({
            '/dev/shm': '/dev/shm',
            '/etc/machine-id': '/etc/machine-id',
            '/run/{}/pulse'.format(uid): '/run/user/1000/pulse',
            '/var/lib/dbus': '/var/lib/dbus',
            '/home/{}/.pulse'.format(user): '/home/phablet/.pulse',
            '/dev/snd': '/dev/snd',
        })

