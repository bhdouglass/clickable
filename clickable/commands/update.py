import subprocess
import shlex

from .base import Command


class UpdateCommand(Command):
    aliases = ['update_docker', 'update-docker']
    name = 'update'
    help = 'Update the docker container for use with clickable'

    def run(self, path_arg=None):
        self.container.check_docker()
        subprocess.check_call(shlex.split('docker pull {}'.format(self.container.base_docker_image)))
