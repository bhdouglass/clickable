import json
import shutil
import os

from .base import Clickable


class GoClickable(Clickable):
    def _ignore(self, path, contents):
        ignored = []
        for content in contents:
            cpath = os.path.abspath(os.path.join(path, content))
            if (
                cpath == os.path.abspath(self.temp) or
                cpath == os.path.abspath(self.config.dir) or
                content in self.config.ignore or
                content == 'clickable.json' or

                # Don't copy the go files, they will be compiled from the source directory
                os.path.splitext(content)[1] == '.go'
            ):
                ignored.append(content)

        return ignored

    def _build(self):
        shutil.copytree(self.cwd, self.temp, ignore=self._ignore)

        gocommand = '/usr/local/go/bin/go build -pkgdir {}/.clickable/go -i -o {}/{} ..'.format(
            self.cwd,
            self.temp,
            self.find_app_name(),
        )
        self.run_container_command(gocommand)
