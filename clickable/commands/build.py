import os
import sys
import shutil

from .base import Command
from .review import ReviewCommand
from clickable.utils import (
    get_builders,
    run_subprocess_check_call,
    makedirs,
    is_sub_dir,
)
from clickable.logger import logger
from clickable.exceptions import ClickableException


class BuildCommand(Command):
    aliases = []
    name = 'build'
    help = 'Compile the app'

    def run(self, path_arg=None):
        try:
            os.makedirs(self.config.build_dir, exist_ok=True)
        except Exception:
            logger.warning('Failed to create the build directory: {}'.format(str(sys.exc_info()[0])))

        try:
            os.makedirs(self.config.build_home, exist_ok=True)
        except Exception:
            logger.warning('Failed to create the build home directory: {}'.format(str(sys.exc_info()[0])))

        self.config.container.setup()

        if self.config.prebuild:
            run_subprocess_check_call(self.config.prebuild, cwd=self.config.cwd, shell=True)

        self.build()

        self.install_additional_files()

        if self.config.postbuild:
            run_subprocess_check_call(self.config.postbuild, cwd=self.config.build_dir, shell=True)

        self.click_build()

        if not self.config.skip_review:
            review = ReviewCommand(self.config)
            review.check(self.click_path, raise_on_error=False)

    def build(self):
        builder_classes = get_builders()
        builder = builder_classes[self.config.builder](self.config, self.device)
        builder.build()

    def install_files(self, pattern, dest_dir):
        if not is_sub_dir(dest_dir, self.config.install_dir):
            dest_dir = os.path.abspath(self.config.install_dir + "/" + dest_dir)

        makedirs(dest_dir)
        if '"' in pattern:
            # Make sure one cannot run random bash code through the "ls" command
            raise ClickableException("install_* patterns must not contain any '\"' quotation character.")

        command = 'ls -d "{}"'.format(pattern)
        files = self.config.container.run_command(command, get_output=True).split()

        logger.info("Installing {}".format(", ".join(files)))
        self.config.container.pull_files(files, dest_dir)

    def install_qml_files(self, pattern, dest_dir):
        if '*' in pattern:
            self.install_files(pattern, dest_dir)
        else:
            command = 'cat {}'.format(os.path.join(pattern, 'qmldir'))
            qmldir = self.config.container.run_command(command, get_output=True)
            module = None
            for line in qmldir.split('\n'):
                if line.startswith('module'):
                    module = line.split(' ')[1]

            if module:
                self.install_files(pattern, os.path.join(
                    dest_dir, *module.split('.')[:-1])
                )
            else:
                self.install_files(pattern, dest_dir)

    def install_additional_files(self):
        for p in self.config.install_lib:
            self.install_files(p, os.path.join(self.config.install_dir,
                                               self.config.app_lib_dir))
        for p in self.config.install_bin:
            self.install_files(p, os.path.join(self.config.install_dir,
                                               self.config.app_bin_dir))
        for p in self.config.install_qml:
            self.install_qml_files(p, os.path.join(self.config.install_dir,
                                               self.config.app_qml_dir))
        for p, dest in self.config.install_data.items():
            self.install_files(p, dest)

    def set_arch(self, manifest):
        arch = manifest.get('architecture', None)

        if arch == '@CLICK_ARCH@' or arch == '':
            manifest['architecture'] = self.config.arch
            return True

        if arch != self.config.arch:
            raise ClickableException('Clickable is building for architecture "{}", but "{}" is specified in the manifest. You can set the architecture field to @CLICK_ARCH@ to let Clickable set the architecture field automatically.'.format(
                self.config.arch, arch))

        return False

    def set_framework(self, manifest):
        framework = manifest.get('framework', None)

        if framework == '@CLICK_FRAMEWORK@' or framework == '':
            manifest['framework'] = self.config.framework
            return True

        if framework != self.config.framework:
            logger.warning('Framework in manifest is "{}", Clickable expected "{}".'.format(
                framework, self.config.framework))

        return False

    def manipulate_manifest(self):
        manifest = self.config.install_files.get_manifest()
        has_changed = False

        if self.set_arch(manifest):
            has_changed = True

        if self.set_framework(manifest):
            has_changed = True

        if has_changed:
            self.config.install_files.write_manifest(manifest)

    def click_build(self):
        self.manipulate_manifest()

        command = 'click build {} --no-validate'.format(self.config.install_dir)
        self.config.container.run_command(command)

        click = self.config.install_files.get_click_filename()
        self.click_path = os.path.join(self.config.build_dir, click)

        if self.config.click_output:
            output_file = os.path.join(self.config.click_output, click)

            if not os.path.exists(self.config.click_output):
                os.makedirs(self.config.click_output)

            shutil.copyfile(self.click_path, output_file)
            self.click_path = output_file

        logger.debug('Click outputted to {}'.format(self.click_path))
