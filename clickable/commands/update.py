import subprocess
import shlex

from .base import Command
from clickable.utils import (
    run_subprocess_check_call,
    run_subprocess_check_output,
)


class UpdateCommand(Command):
    aliases = ['update_docker', 'update-docker']
    name = 'update'
    help = 'Update the docker container for use with clickable'

    def run(self, path_arg=None):
        self.config.container.check_docker()

        command = 'docker pull {}'.format(self.config.container.base_docker_image)
        run_subprocess_check_call(command)

        if 'armhf' in self.config.container.base_docker_image:
            image = self.config.container.base_docker_image.replace('armhf', 'amd64')
            command = 'docker images -q {}'.format(image)
            image_exists = run_subprocess_check_output(command).strip()

            if image_exists:
                command = 'docker pull {}'.format(image)
                run_subprocess_check_call(command)
