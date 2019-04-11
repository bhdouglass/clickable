import os

from clickable.utils import (
    print_warning,
    merge_make_jobs_into_args,
    flexible_string_to_list,
)


class LibConfig(object):
    cwd = os.getcwd()
    config = {}

    QMAKE = 'qmake'
    CMAKE = 'cmake'
    CUSTOM = 'custom'

    arch_triplet_mapping = {
        'armhf': 'arm-linux-gnueabihf',
        'amd64': 'x86_64-linux-gnu',
        'all': 'all'
    }

    replacements = {
        "$ARCH_TRIPLET": "arch_triplet",
        "$NAME": "name",
        "$ROOT": "root_dir",
        "$BUILD_DIR": "dir",
        "$SRC_DIR": "src_dir",
    }
    accepts_placeholders = ["root_dir", "dir", "src_dir",
                            "build", "build_args", "make_args", "postmake", "postbuild", "prebuild"]

    path_keys = ['root_dir', 'dir', 'src_dir']
    required = ['template']
    flexible_lists = ['dependencies', 'dependencies_build',
                      'dependencies_target', 'dependencies_ppa',
                      'build_args', 'make_args']
    templates = [QMAKE, CMAKE, CUSTOM]

    first_docker_info = True
    container_mode = False
    lxd = False
    use_nvidia = False
    custom_docker_image = False
    gopath = None

    install = False

    def __init__(self, name, json_config, arch, root_dir, debug_build):
        self.debug_build = debug_build

        self.config = {
            'name': name,
            'arch': arch,
            'arch_triplet': None,
            'template': None,
            'postmake': None,
            'prebuild': None,
            'build': None,
            'postbuild': None,
            'dir': '$ROOT/build/$NAME/$ARCH_TRIPLET',
            'src_dir': '$ROOT/libs/$NAME',
            'root_dir': root_dir,
            'specificDependencies': False,
            'dependencies': [],
            'dependencies_build': [],
            'dependencies_target': [],
            'dependencies_ppa': [],
            'make_jobs': 0,
            'docker_image': None,
            'build_args': [],
            'make_args': [],
        }

        self.config.update(json_config)

        self.cleanup_config()

        self.config['arch_triplet'] = self.arch_triplet_mapping[self.config['arch']]

        self.substitute_placeholders()

        for key in self.path_keys:
            if self.config[key]:
                self.config[key] = os.path.abspath(self.config[key])

        self.temp = self.config['dir']

        self.check_config_errors()

    def __getattr__(self, name):
        return self.config[name]

    def __setattr__(self, name, value):
        if name in self.config:
            self.config[name] = value
        else:
            super().__setattr__(name, value)

    def substitute_placeholders(self):
        for key in self.accepts_placeholders:
            for sub in self.replacements:
                rep = self.config[self.replacements[sub]]
                if self.config[key]:
                    if isinstance(self.config[key], list):
                        self.config[key] = [val.replace(sub, rep) for val in self.config[key]]
                    else:
                        self.config[key] = self.config[key].replace(sub, rep)

    def cleanup_config(self):
        self.make_args = merge_make_jobs_into_args(make_args=self.make_args, make_jobs=self.make_jobs)

        for key in self.flexible_lists:
            self.config[key] = flexible_string_to_list(self.config[key])

        if self.config['docker_image']:
            self.custom_docker_image = True

        if self.config['dependencies']:
            if self.config['specificDependencies']:
                self.config['dependencies_build'] += self.config['dependencies']
            else:
                self.config['dependencies_target'] += self.config['dependencies']
            print_warning('The params "dependencies" (and possibly "specificDependencies") in your clickable.json are deprecated and will be removed in a future version of Clickable. Use "dependencies_build" and "dependencies_target" instead!')

    def check_config_errors(self):
        if self.config['template'] == self.CUSTOM and not self.config['build']:
            raise ValueError('When using the "custom" template you must specify a "build" in one the lib configs')
