import subprocess
import shlex

from .base import Command
from clickable.utils import run_subprocess_check_call


class UpdateCommand(Command):
    aliases = ['update_docker', 'update-docker']
    name = 'update'
    help = 'Update the docker container for use with clickable'

    def run(self, path_arg=None):
        self.container.check_docker()

        command = 'docker pull {}'.format(self.container.base_docker_image)
        run_subprocess_check_call(command)
