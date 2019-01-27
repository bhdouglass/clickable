import os
import shutil
import sys

from .base import Command
from clickable.utils import (
    print_info,
    print_warning
)


class CleanLibsCommand(Command):
    aliases = []
    name = 'clean-libs'
    help = 'Clean the library build directories'

    def run(self, path_arg=""):

        single_lib = path_arg
        found = False

        for lib in self.config.lib_configs:
            if not single_lib or single_lib == lib.name:
                print_info("Cleaning {}".format(lib.name))
                found = True

                lib.arch = self.config.arch
                if lib.arch in lib.arch_triplets:
                    lib.dir = os.path.join(lib.dir, lib.arch_triplets[lib.arch])

                if os.path.exists(lib.dir):
                    try:
                        shutil.rmtree(lib.dir)
                    except Exception:
                        cls, value, traceback = sys.exc_info()
                        if cls == OSError and 'No such file or directory' in str(value):  # TODO see if there is a proper way to do this
                            pass  # Nothing to do here, the directory didn't exist
                        else:
                            print_warning('Failed to clean the build directory: {}: {}'.format(type, value))
                else:
                    print_info('Nothing to clean. Path does not exist: {}'.format(lib.dir))

        if single_lib and not found:
            raise ValueError('Cannot clean unknown library {}. You may add it to the clickable.json'.format(single_lib))

