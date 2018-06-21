import json
import shutil
import os

from .base import Clickable
from .make import MakeClickable
from .cmake import CMakeClickable
from .qmake import QMakeClickable
from clickable.utils import print_info, find_manifest


class PureQMLMakeClickable(MakeClickable):
    def post_make(self):
        super(PureQMLMakeClickable, self).post_make()

        with open(self.find_manifest(), 'r') as f:
            manifest = {}
            try:
                manifest = json.load(f)
            except ValueError:
                raise ValueError('Failed reading "manifest.json", it is not valid json')

            manifest['architecture'] = 'all'
            with open(self.find_manifest(), 'w') as writer:
                json.dump(manifest, writer, indent=4)


class PureQMLQMakeClickable(PureQMLMakeClickable, QMakeClickable):
    pass


class PureQMLCMakeClickable(PureQMLMakeClickable, CMakeClickable):
    pass


class PureClickable(Clickable):
    def _ignore(self, path, contents):
        ignored = []
        for content in contents:
            cpath = os.path.abspath(os.path.join(path, content))
            # TODO ignore version control directories by default
            if (
                cpath == os.path.abspath(self.temp) or
                cpath == os.path.abspath(self.config.dir) or
                content in self.config.ignore or
                content == 'clickable.json'
            ):
                ignored.append(content)

        return ignored

    def _build(self):
        shutil.copytree(self.cwd, self.temp, ignore=self._ignore)
        print_info('Copied files to temp directory for click building')


class PythonClickable(PureClickable):
    # The only difference between this and the Pure template is that this doesn't force the "all" arch
    pass
