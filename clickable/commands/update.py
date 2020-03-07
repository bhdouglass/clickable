import subprocess
import shlex

from .base import Command
from clickable.utils import (
    run_subprocess_check_call,
    run_subprocess_check_output,
    image_exists,
)

def update_image(image):
    if image_exists(image):
        command = 'docker pull {}'.format(image)
        run_subprocess_check_call(command)


class UpdateCommand(Command):
    aliases = ['update_docker', 'update-docker']
    name = 'update'
    help = 'Update the docker container for use with clickable'

    def run(self, path_arg=None):
        self.config.container.check_docker()

        for image in self.config.container_list:
            update_image(image)
