import os
import shutil
import sys

from .base import Command
from clickable.logger import logger


class CleanCommand(Command):
    aliases = []
    name = 'clean'
    help = 'Clean the build directory'

    def run(self, path_arg=None):
        if os.path.exists(self.config.build_dir):
            try:
                shutil.rmtree(self.config.build_dir)
            except Exception:
                cls, value, traceback = sys.exc_info()
                if cls == OSError and 'No such file or directory' in str(value):  # TODO see if there is a proper way to do this
                    pass  # Nothing to do here, the directory didn't exist
                else:
                    logger.warning('Failed to clean the build directory: {}: {}'.format(type, value))

        if os.path.exists(self.config.install_dir):
            try:
                shutil.rmtree(self.config.install_dir)
            except Exception:
                cls, value, traceback = sys.exc_info()
                if cls == OSError and 'No such file or directory' in str(value):  # TODO see if there is a proper way to do this
                    pass  # Nothing to do here, the directory didn't exist
                else:
                    logger.warning('Failed to clean the temp directory: {}: {}'.format(type, value))
