import os
import sys

from .base import Command
from clickable.utils import print_warning, get_builders, run_subprocess_check_call
from clickable.container import Container

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
                    lib.build_arch = arch
                    
                    try:
                        os.makedirs(lib.dir)
                    except FileExistsError:
                        pass
                    except Exception:
                        print_warning('Failed to create the build directory: {}'.format(str(sys.exc_info()[0])))

                    container = Container(lib)
                    container.setup_dependencies()

                    if lib.prebuild:
                        run_subprocess_check_call(lib.prebuild, cwd=self.config.cwd, shell=True)

                    self.build(lib, container)

                    if lib.postbuild:
                        run_subprocess_check_call(lib.postbuild, cwd=lib.dir, shell=True)

    def build(self, lib, container):
        builder_classes = get_builders()
        builder = builder_classes[lib.template](lib, container, None)
        builder.build()
