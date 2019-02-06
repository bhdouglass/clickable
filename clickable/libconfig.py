import os

from clickable.utils import (
    print_warning
)

class LibConfig(object):
    cwd = os.getcwd()
    config = {}

    QMAKE = 'qmake'
    CMAKE = 'cmake'
    CUSTOM = 'custom'

    required = ['template','name']
    templates = [QMAKE, CMAKE, CUSTOM]
    arch_triplets = { 'armhf': 'arm-linux-gnueabihf',
                      'amd64': 'x86_64-linux-gnu'}

    first_docker_info = True
    container_mode = False
    lxd = False
    use_nvidia = False
    custom_docker_image = False
    gopath = None

    install = False

    def __init__(self, json_config):
        self.config = {
            'postmake': None,
            'prebuild': None,
            'build': None,
            'postbuild': None,
            'dir': None,
            'src_dir': None,
            'specificDependencies': False,  # TODO make this less confusing
            'dependencies': [],
            'make_jobs': 0,
            'docker_image': None,
            'build_args': None,
            'make_args': None,
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
        self.config['dir'] = os.path.join(self.cwd, self.config['dir']) if self.config['dir'] else os.path.join(self.cwd, 'build', self.config['name'])
        self.config['src_dir'] = os.path.join(self.cwd, self.config['src_dir']) if self.config['src_dir'] else os.path.join(self.cwd, 'libs', self.config['name'])
        self.temp = self.config['dir']

    def cleanup_config(self):
        make_args_contains_jobs = self.make_args and any([arg.startswith('-j') for arg in self.make_args.split()])

        if make_args_contains_jobs:
            if self.make_jobs:
                raise ValueError('Conflict in library section: Number of make jobs has been specified by both, "make_args" and "make_jobs"!')
        else:
            make_jobs_arg = '-j'
            if self.make_jobs:
                make_jobs_arg = '{}{}'.format(make_jobs_arg, self.make_jobs)

            if self.make_args:
                self.make_args = '{} {}'.format(self.make_args, make_jobs_arg)
            else:
                self.make_args = make_jobs_arg

        if self.config['docker_image']:
            self.custom_docker_image = True

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

