from .make import MakeBuilder
from clickable.config import Config


class CMakeBuilder(MakeBuilder):
    name = Config.CMAKE

    def make_install(self):
        super().make_install()

        self.container.run_command('make DESTDIR={} install'.format(self.config.temp))

    def build(self):
        command = 'cmake'

        if self.config.build_args:
            command = '{} {}'.format(command, ' '.join(self.config.build_args))

        if self.config.debug_build:
            command = '{} {}'.format(command, '-DCMAKE_BUILD_TYPE=Debug')

        self.container.run_command('{} {}'.format(command, self.config.src_dir))

        super().build()
