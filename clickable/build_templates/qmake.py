from .make import MakeBuilder
from clickable.config import Config


class QMakeBuilder(MakeBuilder):
    name = Config.QMAKE

    def make_install(self):
        super().make_install()

        self.container.run_command('make INSTALL_ROOT={} install'.format(self.config.temp))

    def build(self):
        command = None

        if self.config.build_arch == 'armhf':
            if self.config.container_mode and self.config.is_arm:
                command = 'qmake'
            else:
                command = 'qt5-qmake-arm-linux-gnueabihf'
        elif self.config.build_arch == 'amd64':
            command = 'qmake'
        else:
            raise Exception('{} is not supported by the qmake build yet'.format(self.config.build_arch))

        if self.config.build_args:
            command = '{} {}'.format(command, self.config.build_args)

        self.container.run_command('{} {}'.format(command, self.config.src_dir))

        super().build()
