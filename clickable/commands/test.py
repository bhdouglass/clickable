import os
import shutil

from .base import Command


class TestCommand(Command):
    aliases = []
    name = 'test'
    help = 'Run tests on a virtual screen'

    def run(self, path_arg=None):
        command = 'xvfb-startup {}'.format(self.config.test)

        self.config.container.run_command(command, use_build_dir=False)
