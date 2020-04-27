import json
import shutil
import os

from .base import Builder
from .make import MakeBuilder
from .cmake import CMakeBuilder
from .qmake import QMakeBuilder
from clickable.logger import logger
from clickable.config.project import ProjectConfig
from clickable.config.constants import Constants
from clickable.exceptions import ClickableException


class PureQMLMakeBuilder(MakeBuilder):
    def post_make_install(self):
        super().post_make_install()

        manifest = self.config.install_files.get_manifest()
        manifest['architecture'] = 'all'
        self.config.install_files.write_manifest(manifest)


class PureQMLQMakeBuilder(PureQMLMakeBuilder, QMakeBuilder):
    name = Constants.PURE_QML_QMAKE


class PureQMLCMakeBuilder(PureQMLMakeBuilder, CMakeBuilder):
    name = Constants.PURE_QML_CMAKE


class PureBuilder(Builder):
    name = Constants.PURE

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
            raise ClickableException('Build directory already exists. Please run "clickable clean" before building again!')
        shutil.copytree(self.config.cwd, self.config.install_dir, ignore=self._ignore)
        logger.info('Copied files to install directory for click building')


class PythonBuilder(PureBuilder):
    # The only difference between this and the Pure builder is that this doesn't force the "all" arch
    name = Constants.PYTHON

    def build(self):
        logger.warn('The "python" builder is deprecated, please use "precompiled" instead')
        super().build()


class PrecompiledBuilder(PureBuilder):
    # The only difference between this and the Pure builder is that this doesn't force the "all" arch
    name = Constants.PRECOMPILED
