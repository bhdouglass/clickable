import os
import sys
import subprocess
import inspect
import glob
from os.path import dirname, basename, isfile, join

from .base import Command
from clickable.utils import print_warning
from clickable.build_templates.base import Builder


class BuildCommand(Command):
    aliases = []
    name = 'build'
    help = 'Compile the app'

    def run(self, path_arg=None):
        try:
            os.makedirs(self.config.dir)
        except Exception:
            print_warning('Failed to create the build directory: {}'.format(str(sys.exc_info()[0])))

        self.container.setup_dependencies()

        if self.config.prebuild:
            subprocess.check_call(self.config.prebuild, cwd=self.config.cwd, shell=True)

        self.build()

        if self.config.postbuild:
            subprocess.check_call(self.config.postbuild, cwd=self.config.dir, shell=True)

    def build(self):
        builder_classes = {}
        builder_dir = join(dirname(__file__), '..')
        modules = glob.glob(join(builder_dir, 'build_templates/*.py'))
        builder_modules = [basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]

        for name in builder_modules:
            builder_submodule = __import__('clickable.build_templates.{}'.format(name), globals(), locals(), [name])
            for name, cls in inspect.getmembers(builder_submodule):
                if inspect.isclass(cls) and issubclass(cls, Builder) and cls.name:
                    builder_classes[cls.name] = cls

        template = self.config.get_template()
        builder = builder_classes[template](self.config, self.container, self.device)
        builder.build()
