import os
import shutil
import sys

from .base import Command
from clickable.utils import print_warning


class CleanCommand(Command):
    aliases = []
    name = 'clean'
    help = 'Clean the build directory'

    def run(self, path_arg=None):
        if os.path.exists(self.config.dir):
            try:
                shutil.rmtree(self.config.dir)
            except Exception:
                type, value, traceback = sys.exc_info()
                if type == OSError and 'No such file or directory' in value:  # TODO see if there is a proper way to do this
                    pass  # Nothing to do here, the directory didn't exist
                else:
                    print_warning('Failed to clean the build directory: {}: {}'.format(type, value))

        if os.path.exists(self.config.temp):
            try:
                shutil.rmtree(self.config.temp)
            except Exception:
                type, value, traceback = sys.exc_info()
                if type == OSError and 'No such file or directory' in value:  # TODO see if there is a proper way to do this
                    pass  # Nothing to do here, the directory didn't exist
                else:
                    print_warning('Failed to clean the temp directory: {}: {}'.format(type, value))
