import os
import json
import platform
import xml.etree.ElementTree as ElementTree

from .libconfig import LibConfig

from .utils import (
    find_manifest,
    get_manifest,
    merge_make_jobs_into_args,
    env,
    print_warning,
    print_info,
    ManifestNotFoundException,
)


class Config(object):
    config = {}

    ENV_MAP = {
        'CLICKABLE_ARCH': 'arch',
        'CLICKABLE_TEMPLATE': 'template',
        'CLICKABLE_DIR': 'dir',
        'CLICKABLE_LXD': 'lxd',
        'CLICKABLE_DEFAULT': 'default',
        'CLICKABLE_MAKE_JOBS': 'make_jobs',
        'GOPATH': 'gopath',
        'CARGO_HOME': 'cargo_home',
        'CLICKABLE_DOCKER_IMAGE': 'docker_image',
        'CLICKABLE_BUILD_ARGS': 'build_args',
        'CLICKABLE_MAKE_ARGS': 'make_args',
        'CLICKABLE_DIRTY': 'dirty',
    }

    PURE_QML_QMAKE = 'pure-qml-qmake'
    QMAKE = 'qmake'
    PURE_QML_CMAKE = 'pure-qml-cmake'
    CMAKE = 'cmake'
    CUSTOM = 'custom'
    CORDOVA = 'cordova'
    PURE = 'pure'
    PYTHON = 'python'
    GO = 'go'
    RUST = 'rust'

    required = ['arch', 'dir', 'docker_image']
    depricated = ['chroot', 'sdk', 'package', 'app', 'premake', 'ssh']
    templates = [PURE_QML_QMAKE, QMAKE, PURE_QML_CMAKE, CMAKE, CUSTOM, CORDOVA, PURE, PYTHON, GO, RUST]

    first_docker_info = True
    device_serial_number = None
    ssh = None
    click_output = None
    container_mode = False
    use_nvidia = False
    apikey = None
    is_xenial = True
    custom_docker_image = True
    install = True
    debug_build = False

    def __init__(self, args, desktop=False):
        self.desktop = desktop
        self.cwd = os.getcwd()

        self.config = {
            'arch': 'armhf',
            'template': None,
            'postmake': None,
            'prebuild': None,
            'build': None,
            'postbuild': None,
            'launch': None,
            'dir': './build/',
            'src_dir': self.cwd,
            'kill': None,
            'scripts': {},
            'lxd': False,
            'default': 'clean build click-build install launch',
            'log': None,
            'specificDependencies': False,  # TODO make this less confusing
            'dependencies': [],
            'ignore': [],
            'make_jobs': 0,
            'gopath': None,
            'cargo_home': None,
            'docker_image': None,
            'build_args': None,
            'make_args': None,
            'dirty': False,
            'libraries': [],
        }

        json_config = self.load_json_config()
        self.config.update(json_config)
        env_config = self.load_env_config()
        self.config.update(env_config)
        arg_config = self.load_arg_config(args)
        self.config.update(arg_config)

        self.lib_configs = [LibConfig(lib) for lib in self.config['libraries']]

        self.cleanup_config()

        self.host_arch = platform.machine()
        self.is_arm = self.host_arch.startswith('arm')
        self.temp = os.path.join(self.config['dir'], 'tmp')

        if self.config['dirty']:
            commands = self.config['default'].split()

            if 'clean' in commands:
                commands.remove('clean')
                self.config['default'] = ' '.join(commands)

        self.build_arch = self.config['arch']
        if self.config['template'] == self.PURE_QML_QMAKE or self.config['template'] == self.PURE_QML_CMAKE or self.config['template'] == self.PURE:
            self.build_arch = 'armhf'

        if self.config['arch'] == 'all':
            self.build_arch = 'armhf'

        if self.desktop:
            self.build_arch = 'amd64'

        if not self.config['docker_image']:
            self.custom_docker_image = False
            if self.is_xenial:
                self.config['docker_image'] = 'clickable/ubuntu-sdk:16.04-{}'.format(self.build_arch)
            else:
                self.config['docker_image'] = 'clickable/ubuntu-sdk:15.04-{}'.format(self.build_arch)

        self.check_config_errors()

    def __getattr__(self, name):
        return self.config[name]

    def __setattr__(self, name, value):
        if name in self.config:
            self.config[name] = value
        else:
            super().__setattr__(name, value)

    def load_json_config(self):
        config = {}
        if os.path.isfile(os.path.join(self.cwd, 'clickable.json')):
            with open(os.path.join(self.cwd, 'clickable.json'), 'r') as f:
                config_json = {}
                try:
                    config_json = json.load(f)
                except ValueError:
                    raise ValueError('Failed reading "clickable.json", it is not valid json')

                for key in self.depricated:
                    if key in config_json:
                        raise ValueError('"{}" is a no longer a valid configuration option'.format(key))

                for key in self.config:
                    value = config_json.get(key, None)

                    if value:
                        config[key] = value

        return config

    def load_env_config(self):
        if env('OPENSTORE_API_KEY'):
            self.apikey = env('OPENSTORE_API_KEY')

        if env('CLICKABLE_CONTAINER_MODE'):
            self.container_mode = True

        if env('CLICKABLE_SERIAL_NUMBER'):
            self.device_serial_number = env('CLICKABLE_SERIAL_NUMBER')

        if env('CLICKABLE_SSH'):
            self.ssh = env('CLICKABLE_SSH')

        if env('CLICKABLE_OUTPUT'):
            self.click_output = env('CLICKABLE_OUTPUT')

        if env('CLICKABLE_NVIDIA'):
            self.use_nvidia = True

        if env('CLICKABLE_VIVID'):
            self.is_xenial = False

        if env('CLICKABLE_DEBUG_BUILD'):
            self.debug_build = True

        config = {}
        for var, name in self.ENV_MAP.items():
            if env(var):
                config[name] = env(var)

        return config

    def load_arg_config(self, args):
        if args.serial_number:
            self.device_serial_number = args.serial_number

        if args.ssh:
            self.ssh = args.ssh

        if args.output:
            self.click_output = args.output

        if args.container_mode:
            self.container_mode = args.container_mode

        if args.nvidia:
            self.use_nvidia = args.nvidia

        if args.apikey:
            self.apikey = args.apikey

        if args.vivid:
            self.is_xenial = not args.vivid

        if args.debug_build:
            self.debug_build = True

        config = {}
        if args.arch:
            config['arch'] = args.arch

        if args.lxd:
            config['lxd'] = args.lxd

        if args.docker_image:
            config['docker_image'] = args.docker_image

        if args.dirty:
            config['dirty'] = True

        return config

    def cleanup_config(self):
        self.make_args = merge_make_jobs_into_args(make_args=self.make_args, make_jobs=self.make_jobs)

        if self.desktop:
            self.config['arch'] = 'amd64'
        elif self.config['template'] == self.PURE_QML_CMAKE or self.config['template'] == self.PURE_QML_QMAKE or self.config['template'] == self.PURE:
            self.config['arch'] = 'all'

        self.config['dir'] = os.path.abspath(self.config['dir'])

        if not self.config['kill']:
            if self.config['template'] == self.CORDOVA:
                self.config['kill'] = 'cordova-ubuntu'
            elif self.config['template'] == self.PURE_QML_CMAKE or self.config['template'] == self.PURE_QML_QMAKE or self.config['template'] == self.PURE:
                self.config['kill'] = 'qmlscene'

        if isinstance(self.config['dependencies'], (str, bytes)):
            self.config['dependencies'] = self.config['dependencies'].split(' ')

        if type(self.config['default']) == list:
            self.config['default'] = ' '.join(self.config['default'])

    def check_config_errors(self):
        if self.config['template'] == self.CUSTOM and not self.config['build']:
            raise ValueError('When using the "custom" template you must specify a "build" in the config')
        if self.config['template'] == self.GO and not self.config['gopath']:
            raise ValueError('When using the "go" template you must specify a "gopath" in the config or use the '
                             '"GOPATH"env variable')
        if self.config['template'] == self.RUST and not self.config['cargo_home']:
            raise ValueError('When using the "rust" template you must specify a "cargo_home" in the config or use the '
                             '"CARGO_HOME" env variable')

        if self.config['template'] and self.config['template'] not in self.templates:
            raise ValueError('"{}" is not a valid template ({})'.format(self.config['template'], ', '.join(self.templates)))

        for key in self.required:
            if key not in self.config:
                raise ValueError('"{}" is empty in the config file'.format(key))

    def get_template(self):
        if not self.config['template']:
            template = None
            directory = os.listdir(os.getcwd())

            if 'config.xml' in directory:
                template = Config.CORDOVA

            if not template:
                try:
                    manifest = get_manifest(os.getcwd())
                except ValueError:
                    manifest = None
                except ManifestNotFoundException:
                    manifest = None

            if not template and 'CMakeLists.txt' in directory:
                template = Config.CMAKE

                if manifest and manifest.get('architecture', None) == 'all':
                    template = Config.PURE_QML_CMAKE

            pro_files = [f for f in directory if f.endswith('.pro')]

            if pro_files:
                template = Config.QMAKE

                if manifest and manifest.get('architecture', None) == 'all':
                    template = Config.PURE_QML_QMAKE

            if not template:
                template = Config.PURE

            self.config['template'] = template
            self.cleanup_config()

            print_info('Auto detected template to be "{}"'.format(template))

        return self.config['template']

    def find_manifest(self, ignore_dir=None):
        if self.config['template'] == Config.CORDOVA:
            manifest = find_manifest(self.temp, ignore_dir=ignore_dir)
        else:
            manifest = find_manifest(self.cwd, self.temp, self.config['dir'], ignore_dir)

        return manifest

    def get_manifest(self):
        if self.config['template'] == Config.CORDOVA:
            manifest = get_manifest(self.temp)
        else:
            manifest = get_manifest(self.cwd, self.temp, self.config['dir'])

        return manifest

    def find_version(self):
        if self.config['template'] == Config.CORDOVA:
            tree = ElementTree.parse('config.xml')
            root = tree.getroot()
            version = root.attrib['version'] if 'version' in root.attrib else '1.0.0'
        else:
            version = self.get_manifest().get('version', '1.0')

        return version

    def find_package_name(self):
        if self.config['template'] == Config.CORDOVA:
            tree = ElementTree.parse('config.xml')
            root = tree.getroot()
            package = root.attrib['id'] if 'id' in root.attrib else None

            if not package:
                raise ValueError('No package name specified in config.xml')

        else:
            package = self.get_manifest().get('name', None)

            if not package:
                raise ValueError('No package name specified in manifest.json or clickable.json')

        return package

    def find_app_name(self):
        app = None
        hooks = self.get_manifest().get('hooks', {})
        for key, value in hooks.items():
            if 'desktop' in value:
                app = key
                break

        if not app:  # If we don't find an app with a desktop file just find the first one
            apps = list(hooks.keys())
            if len(apps) > 0:
                app = apps[0]

        if not app:
            raise ValueError('No app name specified in manifest.json or clickable.json')

        return app

    def get_click_filename(self):
        self.get_template()

        return '{}_{}_{}.click'.format(self.find_package_name(), self.find_version(), self.config['arch'])
