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

    flexible_lists = ['dependencies', 'dependencies_build',
                      'dependencies_target', 'dependencies_ppa',
                      'build_args', 'make_args']
    required = ['template']
    templates = [QMAKE, CMAKE, CUSTOM]
    arch_triplets = {
        'armhf': 'arm-linux-gnueabihf',
        'amd64': 'x86_64-linux-gnu'
    }

    first_docker_info = True
    container_mode = False
    lxd = False
    use_nvidia = False
    custom_docker_image = False
    gopath = None

    install = False

    def __init__(self, name, json_config, debug_build):
        self.debug_build = debug_build
        self.name = name

        self.config = {
            'postmake': None,
            'prebuild': None,
            'build': None,
            'postbuild': None,
            'dir': None,
            'src_dir': None,
            'root_dir': self.cwd,
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

        self.check_config_errors()
        self.set_dirs()

    def __getattr__(self, name):
        return self.config[name]

    def __setattr__(self, name, value):
        if name in self.config:
            self.config[name] = value
        else:
            super().__setattr__(name, value)

    def set_dirs(self):
        self.config['dir'] = os.path.join(self.cwd, self.config['dir']) if self.config['dir'] else os.path.join(self.cwd, 'build', self.name)
        self.config['src_dir'] = os.path.join(self.cwd, self.config['src_dir']) if self.config['src_dir'] else os.path.join(self.cwd, 'libs', self.name)
        self.temp = self.config['dir']

    def cleanup_config(self):
        self.make_args = merge_make_jobs_into_args(make_args = self.make_args, make_jobs = self.make_jobs)

        for key in self.flexible_lists:
            self.config[key] = flexible_string_to_list(self.config[key])

        if self.config['docker_image']:
            self.custom_docker_image = True

        if isinstance(self.config['dependencies'], (str, bytes)):
            self.config['dependencies'] = self.config['dependencies'].split(' ')

        if self.config['dependencies']:
            if self.config['specificDependencies']:
                self.config['dependencies_build'] += self.config['dependencies']
            else:
                self.config['dependencies_target'] += self.config['dependencies']
            print_warning('The params "dependencies" (and possibly "specificDependencies") in your clickable.json are deprecated and will be removed in a future version of Clickable. Use "dependencies_build" and "dependencies_target" instead!')

    def check_config_errors(self):
        # TODO Warning may be removed in a future version
        if 'architectures' in self.config:
            print_warning('architectures key in libraries section ignored. Specify the architecture in app section instead.')

        if self.lxd:
            raise ValueError('Building libraries is only supported with docker')

        if self.config['template'] == self.CUSTOM and not self.config['build']:
            raise ValueError('When using the "custom" template you must specify a "build" in one the lib configs')

        if self.config['template'] and self.config['template'] not in self.templates:
            raise ValueError('"{}" is not a valid template for libraries ({})'.format(self.config['template'], ', '.join(self.templates)))

        for key in self.required:
            if key not in self.config:
                raise ValueError('"{}" is empty in one of the library configs'.format(key))
