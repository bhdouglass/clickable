import os
import sys
import shutil

from .base import Command
from clickable.utils import (
    get_builders,
    run_subprocess_check_call,
    makedirs,
)
from clickable.logger import logger
from clickable.exceptions import ClickableException


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
            logger.warning('Failed to create the build directory: {}'.format(str(sys.exc_info()[0])))

        self.config.container.setup()

        if self.config.prebuild:
            run_subprocess_check_call(self.config.prebuild, cwd=self.config.cwd, shell=True)

        self.build()

        self.install_additional_files()

        if self.config.postbuild:
            run_subprocess_check_call(self.config.postbuild, cwd=self.config.build_dir, shell=True)

        self.click_build()

    def build(self):
        template = self.config.get_template()

        builder_classes = get_builders()
        builder = builder_classes[template](self.config, self.device)
        builder.build()

    def install_files(self, pattern, dest_dir):
        logger.info("Installing {}".format(pattern))
        makedirs(dest_dir)
        command = 'cp -r {} {}'.format(pattern, dest_dir)
        self.config.container.run_command(command)

    def install_additional_files(self):
        for p in self.config.install_lib:
            self.install_files(p, os.path.join(self.config.install_dir,
                                               self.config.app_lib_dir))
        for p in self.config.install_bin:
            self.install_files(p, os.path.join(self.config.install_dir,
                                               self.config.app_bin_dir))
        for p in self.config.install_qml:
            self.install_files(p, os.path.join(self.config.install_dir,
                                               self.config.app_qml_dir))
        for p, dest in self.config.install_data.items():
            self.install_files(p, dest)

    def set_arch(self):
        manifest = self.config.get_manifest()

        arch = manifest.get('architecture', None)
        if arch == '@CLICK_ARCH@':
            arch = self.config.arch
            manifest['architecture'] = arch
            self.config.write_manifest(manifest)

        if arch != self.config.arch and arch != 'all':
            raise ClickableException('Clickable is building for architecture "{}", but "{}" is specified in the manifest. You may set the architecture field to @CLICK_ARCH@ to let Clickable set the architecture field automatically.'.format(
                self.config.arch, arch))

    def click_build(self):
        self.set_arch()

        command = 'click build {} --no-validate'.format(self.config.install_dir)
        self.config.container.run_command(command)

        click = self.config.get_click_filename()
        click_path = os.path.join(self.config.build_dir, click)

        if self.config.click_output:
            output_file = os.path.join(self.config.click_output, click)

            if not os.path.exists(self.config.click_output):
                os.makedirs(self.config.click_output)

            shutil.copyfile(click_path, output_file)
            click_path = output_file

        logger.debug('Click outputted to {}'.format(click_path))
