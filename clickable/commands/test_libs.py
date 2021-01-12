import os

from .base import Command
from clickable.logger import logger
from clickable.container import Container
from clickable.exceptions import ClickableException


class TestLibsCommand(Command):
    aliases = []
    name = 'test-libs'
    help = 'Run tests on libraries'

    def run(self, path_arg=""):
        if not self.config.lib_configs:
            logger.warning('No libraries defined.')

        single_lib = path_arg
        found = False

        for lib in self.config.lib_configs:
            if not single_lib or single_lib == lib.name:
                logger.info("Running tests on {}".format(lib.name))
                found = True

                self.run_test(lib)

        if single_lib and not found:
            raise ClickableException('Cannot test unknown library {}. You may add it to the clickable.json'.format(single_lib))

    def run_test(self, lib):
        if not os.path.exists(lib.build_dir):
            logger.warning("Library {} has not yet been built for host architecture.".format(lib.name))
        else:
            lib.container_mode = self.config.container_mode
            lib.docker_image = self.config.docker_image
            lib.build_arch = self.config.build_arch
            lib.container = Container(lib, lib.name)
            lib.container.setup()

            # This is a workaround for lib env vars being overwritten by
            # project env vars, especially affecting Container Mode.
            lib.set_env_vars()

            command = 'xvfb-startup {}'.format(lib.test)
            lib.container.run_command(command, use_build_dir=True)

