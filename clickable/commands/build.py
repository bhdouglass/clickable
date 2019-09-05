import os
import sys
import shutil

from .base import Command
from clickable.utils import (
    print_warning,
    print_info,
    get_builders,
    run_subprocess_check_call,
)


class BuildCommand(Command):
    aliases = []
    name = 'build'
    help = 'Compile the app'

    def run(self, path_arg=None):
        try:
            os.makedirs(self.config.build_dir)
        except FileExistsError:
            pass
        except Exception:
            print_warning('Failed to create the build directory: {}'.format(str(sys.exc_info()[0])))

        self.config.container.setup_dependencies()

        if self.config.prebuild:
            run_subprocess_check_call(self.config.prebuild, cwd=self.config.cwd, shell=True)

        self.build()

        if self.config.postbuild:
            run_subprocess_check_call(self.config.postbuild, cwd=self.config.build_dir, shell=True)

        self.click_build()

    def build(self):
        template = self.config.get_template()

        builder_classes = get_builders()
        builder = builder_classes[template](self.config, self.device)
        builder.build()

    def click_build(self):
        command = 'click build {} --no-validate'.format(os.path.dirname(self.config.find_manifest()))

        self.config.container.run_command(command)

        if self.config.click_output:
            click = self.config.get_click_filename()
            click_path = os.path.join(self.config.build_dir, click)
            output_file = os.path.join(self.config.click_output, click)

            if not os.path.exists(self.config.click_output):
                os.makedirs(self.config.click_output)

            print_info('Click outputted to {}'.format(output_file))
            shutil.copyfile(click_path, output_file)
