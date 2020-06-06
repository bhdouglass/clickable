import os
import sys

from .base import Command
from clickable.logger import logger
from clickable.utils import get_builders, run_subprocess_check_call
from clickable.container import Container
from clickable.exceptions import ClickableException


class LibBuildCommand(Command):
    aliases = []
    name = 'build-libs'
    help = 'Compile the library dependencies'

    def run(self, path_arg=""):
        if not self.config.lib_configs:
            logger.warning('No libraries defined.')

        single_lib = path_arg
        found = False

        for lib in self.config.lib_configs:
            if not single_lib or single_lib == lib.name:
                logger.info("Building {}".format(lib.name))
                found = True

                lib.container_mode = self.config.container_mode
                lib.docker_image = self.config.docker_image
                lib.build_arch = self.config.build_arch
                lib.container = Container(lib, lib.name)
                lib.container.setup()

                # This is a workaround for lib env vars being overwritten by
                # project env vars, especially affecting Container Mode.
                lib.set_env_vars()

                try:
                    os.makedirs(lib.build_dir, exist_ok=True)
                except Exception:
                    logger.warning('Failed to create the build directory: {}'.format(str(sys.exc_info()[0])))

                try:
                    os.makedirs(lib.build_home, exist_ok=True)
                except Exception:
                    logger.warning('Failed to create the build home directory: {}'.format(str(sys.exc_info()[0])))

                if lib.prebuild:
                    run_subprocess_check_call(lib.prebuild, cwd=self.config.cwd, shell=True)

                self.build(lib)

                if lib.postbuild:
                    run_subprocess_check_call(lib.postbuild, cwd=lib.build_dir, shell=True)

        if single_lib and not found:
            raise ClickableException('Cannot build unknown library {}, which is not in your clickable.json'.format(single_lib))

    def build(self, lib):
        builder_classes = get_builders()
        builder = builder_classes[lib.builder](lib, None)
        builder.build()
