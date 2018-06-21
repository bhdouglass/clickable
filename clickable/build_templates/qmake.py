from .make import MakeClickable


class QMakeClickable(MakeClickable):
    def make_install(self):
        super(QMakeClickable, self).make_install()

        self.run_container_command('make INSTALL_ROOT={} install'.format(self.temp))

    def _build(self):
        command = None

        if self.build_arch == 'armhf':
            command = 'qt5-qmake-arm-linux-gnueabihf'
        elif self.build_arch == 'amd64':
            command = 'qmake'
        else:
            raise Exception('{} is not supported by the qmake build yet'.format(self.build_arch))

        self.run_container_command('{} {}'.format(command, self.cwd))

        super(QMakeClickable, self)._build()
