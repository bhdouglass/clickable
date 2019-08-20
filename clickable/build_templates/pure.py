import json
import shutil
import os

from .base import Builder
from .make import MakeBuilder
from .cmake import CMakeBuilder
from .qmake import QMakeBuilder
from clickable.utils import print_info, find_manifest
from clickable.config import Config


class PureQMLMakeBuilder(MakeBuilder):
    def post_make(self):
        super().post_make()

        manifest_file = self.config.find_manifest(ignore_dir=self.config.install_dir)
        with open(manifest_file, 'r') as f:
            manifest = {}
            try:
                manifest = json.load(f)
            except ValueError:
                raise ValueError('Failed reading "manifest.json", it is not valid json')

            manifest['architecture'] = 'all'
            with open(manifest_file, 'w') as writer:
                json.dump(manifest, writer, indent=4)


class PureQMLQMakeBuilder(PureQMLMakeBuilder, QMakeBuilder):
    name = Config.PURE_QML_QMAKE


class PureQMLCMakeBuilder(PureQMLMakeBuilder, CMakeBuilder):
    name = Config.PURE_QML_CMAKE


class PureBuilder(Builder):
    name = Config.PURE

    def _ignore(self, path, contents):
        ignored = []
        for content in contents:
            cpath = os.path.abspath(os.path.join(path, content))

            if (
                cpath == os.path.abspath(self.config.install_dir) or
                cpath == os.path.abspath(self.config.build_dir) or
                content in self.config.ignore or
                content == 'clickable.json'
            ):
                ignored.append(content)

        return ignored

    def build(self):
        if os.path.isdir(self.config.install_dir):
            raise ValueError('Build directory already exists. Please run "clickable clean" before building again!')
        shutil.copytree(self.config.cwd, self.config.install_dir, ignore=self._ignore)
        print_info('Copied files to install directory for click building')


class PythonBuilder(PureBuilder):
    # The only difference between this and the Pure template is that this doesn't force the "all" arch
    name = Config.PYTHON
