import os
import sys

from clickable.utils import (
    print_info,
    print_warning
)


from .base import Command
from clickable.utils import print_warning, get_builders, run_subprocess_check_call
from clickable.container import Container


class LibBuildCommand(Command):
    aliases = []
    name = 'build-libs'
    help = 'Compile the library dependencies'

    def run(self, path_arg=""):
        if not self.config.lib_configs:
            print_warning('No libraries defined.')

        single_lib = path_arg
        found = False

        for lib in self.config.lib_configs:
            if not single_lib or single_lib == lib.name:
                print_info("Building {}".format(lib.name))
                found = True

                dir_tmp = lib.dir
                lib.arch = self.config.arch
                lib.build_arch = self.config.build_arch
		lib.container_mode = self.config.container_mode
                
		if lib.arch in lib.arch_triplets:
                    lib.dir = os.path.join(dir_tmp, lib.arch_triplets[lib.arch])
                    if not lib.custom_docker_image:
                        if self.config.is_xenial:
                            lib.docker_image = 'clickable/ubuntu-sdk:16.04-{}'.format(lib.arch)
                        else:
                            lib.docker_image = 'clickable/ubuntu-sdk:15.04-{}'.format(lib.arch)
                else:
                  print_warning('Building library for unkown architecture {}'.format(lib.arch))

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

        if single_lib and not found:
            raise ValueError('Unknown library {}. You may add it to the clickable.json'.format(single_lib))

    def build(self, lib, container):
        builder_classes = get_builders()
        builder = builder_classes[lib.template](lib, container, None)
        builder.build()
