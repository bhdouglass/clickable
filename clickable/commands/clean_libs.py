import os
import shutil
import sys

from .base import Command
from clickable.logger import logger
from clickable.exceptions import ClickableException


class CleanLibsCommand(Command):
    aliases = []
    name = 'clean-libs'
    help = 'Clean the library build directories'

    def run(self, path_arg=""):

        single_lib = path_arg
        found = False

        for lib in self.config.lib_configs:
            if not single_lib or single_lib == lib.name:
                logger.info("Cleaning {}".format(lib.name))
                found = True

                if os.path.exists(lib.build_dir):
                    try:
                        shutil.rmtree(lib.build_dir)
                    except Exception:
                        cls, value, traceback = sys.exc_info()
                        if cls == OSError and 'No such file or directory' in str(value):  # TODO see if there is a proper way to do this
                            pass  # Nothing to do here, the directory didn't exist
                        else:
                            logger.warning('Failed to clean the build directory: {}: {}'.format(type, value))
                else:
                    logger.warning('Nothing to clean. Path does not exist: {}'.format(lib.build_dir))

        if single_lib and not found:
            raise ClickableException('Cannot clean unknown library {}. You may add it to the clickable.json'.format(single_lib))

