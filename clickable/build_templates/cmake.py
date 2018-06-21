from .make import MakeClickable


class CMakeClickable(MakeClickable):
    def make_install(self):
        super(CMakeClickable, self).make_install()

        self.run_container_command('make DESTDIR={} install'.format(self.temp))

    def _build(self):
        self.run_container_command('cmake {}'.format(self.cwd))

        super(CMakeClickable, self)._build()
