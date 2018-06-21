import subprocess
import shutil
import sys
import os

from .base import Clickable
from clickable.utils import print_warning


class MakeClickable(Clickable):
    def pre_make(self):
        if self.config.premake:
            subprocess.check_call(self.config.premake, cwd=self.config.dir, shell=True)

    def post_make(self):
        if self.config.postmake:
            subprocess.check_call(self.config.postmake, cwd=self.config.dir, shell=True)

    def make(self):
        command = 'make -j'
        if self.config.make_jobs:
            command = '{}{}'.format(command, self.config.make_jobs)

        self.run_container_command(command)

    def make_install(self):
        if os.path.exists(self.temp) and os.path.isdir(self.temp):
            shutil.rmtree(self.temp)

        try:
            os.makedirs(self.temp)
        except FileExistsError:
            print_warning('Failed to create temp dir, already exists')
        except Exception:
            print_warning('Failed to create temp dir ({}): {}'.format(self.temp, str(sys.exc_info()[0])))

        # The actual make command is implemented in the subclasses

    def _build(self):
        self.pre_make()
        self.make()
        self.post_make()
        self.make_install()
