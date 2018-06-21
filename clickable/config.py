import os
import json

from clickable.utils import (
    print_info,
    print_warning,
    ManifestNotFoundException,
    get_manifest
)


class Config(object):
    config = {
        'package': None,
        'app': None,
        'sdk': 'ubuntu-sdk-15.04',
        'arch': 'armhf',
        'template': None,
        'premake': None,
        'postmake': None,
        'prebuild': None,
        'build': None,
        'postbuild': None,
        'launch': None,
        'dir': './build/',
        'ssh': False,
        'kill': None,
        'scripts': {},
        'chroot': False,
        'lxd': False,
        'default': 'kill clean build click-build install launch',
        'log': None,
        'specificDependencies': False,  # TODO make this less confusing
        'dependencies': [],
        'ignore': [],
        'make_jobs': 0,
        'gopath': None,
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

    required = ['sdk', 'arch', 'dir']
    templates = [PURE_QML_QMAKE, QMAKE, PURE_QML_CMAKE, CMAKE, CUSTOM, CORDOVA, PURE, PYTHON, GO]

    def __init__(self, ip=None, arch=None, template=None, skip_detection=False, lxd=False, click_output=None, container_mode=False, desktop=False, sdk=None, use_nvidia=False):
        self.skip_detection = skip_detection
        self.click_output = click_output
        self.desktop = desktop
        self.use_nvidia = use_nvidia
        self.cwd = os.getcwd()
        self.load_config()

        self.container_mode = container_mode
        if 'CLICKABLE_CONTAINER_MODE' in os.environ and os.environ['CLICKABLE_CONTAINER_MODE']:
            self.container_mode = True

        if ip:
            self.ssh = ip

        if self.desktop:
            self.arch = 'amd64'
        elif arch:
            self.arch = arch

        if template:
            self.template = template

        if lxd:
            self.lxd = lxd

        if sdk:
            self.sdk = sdk

        if not self.gopath and 'GOPATH' in os.environ and os.environ['GOPATH']:
            self.gopath = os.environ['GOPATH']

        if skip_detection:
            if not template:
                self.template = self.PURE
        else:
            self.detect_template()

        if not self.kill:
            if self.template == self.CORDOVA:
                self.kill = 'cordova-ubuntu'
            elif self.template == self.PURE_QML_CMAKE or self.template == self.PURE_QML_QMAKE or self.template == self.PURE:
                self.kill = 'qmlscene'
            else:
                # TODO grab app name from manifest
                self.kill = self.app

        if self.template == self.PURE_QML_CMAKE or self.template == self.PURE_QML_QMAKE or self.template == self.PURE:
            self.arch = 'all'

        if self.template == self.CUSTOM and not self.build:
            raise ValueError('When using the "custom" template you must specify a "build" in the config')
        if self.template == self.GO and not self.gopath:
            raise ValueError('When using the "go" template you must specify a "gopath" in the config or use the "GOPATH" env variable')

        if self.template not in self.templates:
            raise ValueError('"{}" is not a valid template ({})'.format(self.template, ', '.join(self.templates)))

        if isinstance(self.dependencies, (str, bytes)):
            self.dependencies = self.dependencies.split(' ')

        if type(self.default) == list:
            self.default = ' '.join(self.default)

    def __getattr__(self, name):
        return self.config[name]

    def __setattr__(self, name, value):
        self.config[name] = value

    def load_config(self, file='clickable.json'):
        if os.path.isfile(os.path.join(self.cwd, file)):
            with open(os.path.join(self.cwd, file), 'r') as f:
                config_json = {}
                try:
                    config_json = json.load(f)
                except ValueError:
                    raise ValueError('Failed reading "{}", it is not valid json'.format(file))

                for key in self.config:
                    value = config_json.get(key, None)

                    if value:
                        self.config[key] = value
        else:
            if not self.skip_detection:
                print_warning('No clickable.json was found, using defaults and cli args')

        for key in self.required:
            if not getattr(self, key):
                raise ValueError('"{}" is empty in the config file'.format(key))

        self.dir = os.path.abspath(self.dir)

    def detect_template(self):
        if not self.template:
            template = None

            try:
                manifest = get_manifest(os.getcwd())
            except ValueError:
                manifest = None
            except ManifestNotFoundException:
                manifest = None

            directory = os.listdir(os.getcwd())
            if not template and 'CMakeLists.txt' in directory:
                template = Config.CMAKE

                if manifest and manifest.get('architecture', None) == 'all':
                    template = Config.PURE_QML_CMAKE

            pro_files = [f for f in directory if f.endswith('.pro')]

            if pro_files:
                template = Config.QMAKE

                if manifest and manifest.get('architecture', None) == 'all':
                    template = Config.PURE_QML_QMAKE

            if not template and 'config.xml' in directory:
                template = Config.CORDOVA

            if not template:
                template = Config.PURE

            self.template = template
            print_info('Auto detected template to be "{}"'.format(template))
