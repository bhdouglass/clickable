import os
import sys

from .base import Command
from clickable.utils import print_warning, get_builders, run_subprocess_check_call


class BuildCommand(Command):
    aliases = []
    name = 'build'
    help = 'Compile the app'

    def run(self, path_arg=None):
        try:
            os.makedirs(self.config.dir)
        except FileExistsError:
            pass
        except Exception:
            print_warning('Failed to create the build directory: {}'.format(str(sys.exc_info()[0])))

        self.container.setup_dependencies()

        if self.config.prebuild:
            run_subprocess_check_call(self.config.prebuild, cwd=self.config.cwd, shell=True)

        self.build()

        if self.config.postbuild:
            run_subprocess_check_call(self.config.postbuild, cwd=self.config.dir, shell=True)

    def build(self):
        template = self.config.get_template()

        builder_classes = get_builders()
        builder = builder_classes[template](self.config, self.container, self.device)
        builder.build()
