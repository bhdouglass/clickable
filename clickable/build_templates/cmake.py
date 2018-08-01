from .make import MakeClickable


class CMakeClickable(MakeClickable):
    def make_install(self):
        super(CMakeClickable, self).make_install()

        self.run_container_command('make DESTDIR={} install'.format(self.temp))

    def _build(self):
        command = 'cmake'

        if self.config.conf_opts:
            command = '{} {}'.format(command, self.config.conf_opts)

        self.run_container_command('{} {}'.format(command, self.cwd))

        super(CMakeClickable, self)._build()
