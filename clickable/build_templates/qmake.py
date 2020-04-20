from .make import MakeBuilder
from clickable.config.project import ProjectConfig
from clickable.config.constants import Constants
from clickable.exceptions import ClickableException

qmake_arch_spec_mapping = {
    'amd64': 'linux-g++',
    'armhf': 'ubuntu-arm-gnueabihf-g++',
    'arm64': 'linux-aarch64-gnu-g++'
}

class QMakeBuilder(MakeBuilder):
    name = Constants.QMAKE

    def make_install(self):
        super().make_install()

        self.config.container.run_command('make INSTALL_ROOT={} install'.format(self.config.install_dir))

    def build(self):
        command = '/usr/bin/qmake -qt5'

        if not self.config.build_arch in qmake_arch_spec_mapping:
            raise ClickableException('{} is not supported by the qmake build yet'.format(self.config.build_arch))

        arch_spec = qmake_arch_spec_mapping[self.config.build_arch]
        arch_triplet = Constants.arch_triplet_mapping[self.config.build_arch]
        conf_path = '/usr/lib/{}/qt5/qt.conf'.format(arch_triplet)
        spec_path = '/usr/lib/{}/qt5/mkspecs/{}'.format(arch_triplet, arch_spec)

        command = '{} -- -qtconf {} -spec {}'.format(
                command,
                conf_path,
                spec_path)

        if self.config.build_args:
            command = '{} {}'.format(command, ' '.join(self.config.build_args))

        if self.config.debug_build:
            command = '{} {}'.format(command, 'CONFIG+=debug')

        self.config.container.run_command('{} {}'.format(command, self.config.src_dir))

        super().build()
