import os
import shutil
import sys

from .base import Command
from clickable.utils import print_warning


class CleanLibsCommand(Command):
    aliases = []
    name = 'clean-libs'
    help = 'Clean the library build directories'

    def run(self, path_arg=None):
        for lib in self.config.lib_configs:
            if os.path.exists(lib.dir):
                try:
                    shutil.rmtree(lib.dir)
                except Exception:
                    cls, value, traceback = sys.exc_info()
                    if cls == OSError and 'No such file or directory' in str(value):  # TODO see if there is a proper way to do this
                        pass  # Nothing to do here, the directory didn't exist
                    else:
                        print_warning('Failed to clean the build directory: {}: {}'.format(type, value))

