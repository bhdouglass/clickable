from .make import MakeBuilder
from clickable.config.project import ProjectConfig
from clickable.config.constants import Constants
from clickable.exceptions import ClickableException

class QMakeBuilder(MakeBuilder):
    name = Constants.QMAKE

    def make_install(self):
        super().make_install()

        self.config.container.run_command('make INSTALL_ROOT={}/ install'.format(self.config.install_dir))

    def build(self):
        if self.config.arch == self.config.host_arch or self.config.qt_version == "5.9":
            command = 'qmake'
        else:
            command = '/usr/lib/{}/qt5/bin/qmake'.format(self.config.arch_triplet)

        if self.config.build_args:
            command = '{} {}'.format(command, ' '.join(self.config.build_args))

        if self.config.debug_build:
            command = '{} {}'.format(command, 'CONFIG+=debug')

        # user may have defined a specific .pro file, so qmake must not read others (if any)
        if not any(arg.endswith(".pro") for arg in self.config.build_args):
            command = '{} {}'.format(command, self.config.src_dir)

        self.config.container.run_command(command)

        super().build()
