import os
import shutil

from .base import Command
from clickable.utils import print_info


class TestCommand(Command):
    aliases = []
    name = 'test'
    help = 'Run tests on a virtual screen'

    def run(self, path_arg=None):
        command = 'xvfb-startup {}'.format(self.config.test)

        self.config.container.run_command(command, use_dir=False)
