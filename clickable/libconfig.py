#TODO check imports
import os


class LibConfig(object):
    cwd = os.getcwd()
    config = {}

    QMAKE = 'qmake'
    CMAKE = 'cmake'
    CUSTOM = 'custom'

    required = ['template']
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
        # TODO Check which configs are used in the builders 
        self.config = {
            'architectures': ['armhf'],
            'template': None,
            'postmake': None,
            'prebuild': None,
            'build': None,
            'postbuild': None,
            'name': None,
            'dir': None,
            'src_dir': None,
            'specificDependencies': False,  # TODO make this less confusing
            'dependencies': [],
            'make_jobs': 0,
            'docker_image': None,
            'build_args': None,
        }

        self.config.update(json_config)

        if self.config['docker_image']:
            self.custom_docker_image = True

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
        self.config['dir'] = self.config['dir'] if self.config['dir'] else os.path.join(self.cwd, 'build', self.config['name'])
        self.config['src_dir'] = self.config['src_dir'] if self.config['src_dir'] else os.path.join(self.cwd, 'libs', self.config['name'])
        self.temp = self.config['dir']

    def check_config_errors(self):
        if self.lxd:
            raise ValueError('Building libraries is only supported with docker')

        if not self.config['name'] and not (self.config['dir'] and self.config['src_dir']):
            raise ValueError('Either "name" must be specified or "dir" and "src_dir" in each lib config')

        if self.config['template'] == self.CUSTOM and not self.config['build']:
            raise ValueError('When using the "custom" template you must specify a "build" in one the lib configs')

        if self.config['template'] and self.config['template'] not in self.templates:
            raise ValueError('"{}" is not a valid template for libraries ({})'.format(self.config['template'], ', '.join(self.templates)))

        for key in self.required:
            if key not in self.config:
                raise ValueError('"{}" is empty in one of the library configs'.format(key))

        if self.custom_docker_image and len(architectures) > 1:
            raise ValueError('There can only be one architecture specified when providing a custom docker_image in the library config'.format(key))

