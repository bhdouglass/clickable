import os
import sys
import subprocess
import inspect
import glob
from os.path import dirname, basename, isfile, join

from .base import Command
from clickable.utils import print_warning
from clickable.build_templates.base import Builder
from clickable.container import Container
from clickable.device import Device

class LibBuildCommand(Command):
    aliases = []
    name = 'build-libs'
    help = 'Compile the library dependencies'

    def run(self, path_arg=None):
        if not self.config.lib_configs:
            print_warning('No libraries defined.')

        for lib in self.config.lib_configs:
            dir_tmp = lib.dir
            for arch in lib.architectures:
                if arch in lib.arch_triplets:
                    if not lib.custom_docker_image:
                        if self.config.is_xenial:
                            lib.docker_image = 'clickable/ubuntu-sdk:16.04-{}'.format(arch)
                        else:
                            lib.docker_image = 'clickable/ubuntu-sdk:15.04-{}'.format(arch)
                    lib.dir = os.path.join(dir_tmp, lib.arch_triplets[arch])
                    lib.arch = arch
                    
                    try:
                        os.makedirs(lib.dir)
                    except FileExistsError:
                        pass
                    except Exception:
                        print_warning('Failed to create the build directory: {}'.format(str(sys.exc_info()[0])))

                    if lib.prebuild:
                        subprocess.check_call(lib.prebuild, cwd=self.config.cwd, shell=True)

                    self.build(lib)

                    if lib.postbuild:
                        subprocess.check_call(lib.postbuild, cwd=lib.dir, shell=True)

    def build(self, lib):
        container = Container(lib)
        container.setup_dependencies()

        builder_classes = {}
        builder_dir = join(dirname(__file__), '..')
        modules = glob.glob(join(builder_dir, 'build_templates/*.py'))
        builder_modules = [basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]

        for name in builder_modules:
            builder_submodule = __import__('clickable.build_templates.{}'.format(name), globals(), locals(), [name])
            for name, cls in inspect.getmembers(builder_submodule):
                if inspect.isclass(cls) and issubclass(cls, Builder) and cls.name:
                    builder_classes[cls.name] = cls

        builder = builder_classes[lib.template](lib, container, None)
        builder.build()
