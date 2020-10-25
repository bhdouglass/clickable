from .make import MakeBuilder
from clickable.config.project import ProjectConfig
from clickable.config.constants import Constants


class CMakeBuilder(MakeBuilder):
    name = Constants.CMAKE

    def make_install(self):
        super().make_install()

        self.config.container.run_command('make DESTDIR={}/ install'.format(self.config.install_dir))

    def build(self):
        command = 'cmake'

        if self.config.build_args:
            command = '{} {}'.format(command, ' '.join(self.config.build_args))

        if self.config.debug_build:
            command = '{} {}'.format(command, '-DCMAKE_BUILD_TYPE=Debug')
        else:
            command = '{} {}'.format(command, '-DCMAKE_BUILD_TYPE=Release')

        self.config.container.run_command('{} {} -DCMAKE_INSTALL_PREFIX:PATH=/.'.format(command, self.config.src_dir))

        super().build()
