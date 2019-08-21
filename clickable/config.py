import os
import json
import platform
import re
import xml.etree.ElementTree as ElementTree

from .libconfig import LibConfig

from .utils import (
    find_manifest,
    get_manifest,
    get_desktop,
    merge_make_jobs_into_args,
    flexible_string_to_list,
    env,
    print_warning,
    print_info,
    FileNotFoundException,
    validate_clickable_json,
)


class Config(object):
    config = {}

    ENV_MAP = {
        'CLICKABLE_ARCH': 'arch',
        'CLICKABLE_TEMPLATE': 'template',
        'CLICKABLE_BUILD_DIR': 'build_dir',
        'CLICKABLE_LXD': 'lxd',
        'CLICKABLE_DEFAULT': 'default',
        'CLICKABLE_MAKE_JOBS': 'make_jobs',
        'GOPATH': 'gopath',
        'CARGO_HOME': 'cargo_home',
        'CLICKABLE_DOCKER_IMAGE': 'docker_image',
        'CLICKABLE_BUILD_ARGS': 'build_args',
        'CLICKABLE_MAKE_ARGS': 'make_args',
        'CLICKABLE_DIRTY': 'dirty',
        'CLICKABLE_TEST': 'test',
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

    container_mapping = {
        ('15.04', 'armhf'): 'clickable/ubuntu-sdk:15.04-armhf',
        ('16.04', 'armhf'): 'clickable/ubuntu-sdk:16.04-armhf',
        ('15.04', 'amd64'): 'clickable/ubuntu-sdk:15.04-amd64',
        ('16.04', 'amd64'): 'clickable/ubuntu-sdk:16.04-amd64',
        ('16.04', 'amd64-nvidia'): 'clickable/ubuntu-sdk:16.04-amd64-nvidia',
    }

    container_list = list(container_mapping.values())

    arch_triplet_mapping = {
        'armhf': 'arm-linux-gnueabihf',
        'amd64': 'x86_64-linux-gnu',
        'all': 'all'
    }

    replacements = {
        "$ARCH_TRIPLET": "arch_triplet",
        "$ROOT": "root_dir",
        "$BUILD_DIR": "build_dir",
        "$SRC_DIR": "src_dir",
        "$INSTALL_DIR": "install_dir",
    }
    accepts_placeholders = ["root_dir", "build_dir", "src_dir", "install_dir",
                            "gopath", "cargo_home", "scripts", "build",
                            "build_args", "make_args", "postmake", "postbuild",
                            "prebuild"]

    path_keys = ['root_dir', 'build_dir', 'src_dir', 'install_dir',
                 'cargo_home', 'gopath']
    required = ['arch', 'build_dir', 'docker_image']
    flexible_lists = ['dependencies', 'dependencies_build',
                      'dependencies_target', 'dependencies_ppa',
                      'build_args', 'make_args', 'default', 'ignore']
    deprecated = ['chroot', 'sdk', 'package', 'app', 'premake', 'ssh']  # TODO add 'dependencies' and 'specificDependencies'
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
    debug = False
    debug_build = False
    debug_gdb = False
    debug_gdb_port = None

    def __init__(self, args, clickable_version, desktop=False):
        self.desktop = desktop
        self.clickable_version = clickable_version
        self.cwd = os.getcwd()

        self.config = {
            'clickable_minimum_required': None,
            'arch': 'armhf',
            'arch_triplet': None,
            'template': None,
            'postmake': None,
            'prebuild': None,
            'build': None,
            'postbuild': None,
            'launch': None,
            'dir': None,
            'build_dir': '$ROOT/build',
            'src_dir': '$ROOT',
            'root_dir': self.cwd,
            'kill': None,
            'scripts': {},
            'lxd': False,
            'default': 'clean build click-build install launch',
            'log': None,
            'specificDependencies': False,
            'dependencies': [],
            'dependencies_build': [],
            'dependencies_target': [],
            'dependencies_ppa': [],
            'ignore': [],
            'make_jobs': 0,
            'gopath': None,
            'cargo_home': os.path.expanduser('~/.cargo'),
            'docker_image': None,
            'build_args': [],
            'make_args': [],
            'dirty': False,
            'libraries': {},
            'test': 'qmltestrunner',
            'install_dir': '$BUILD_DIR/install'
        }

        json_config = self.load_json_config(args.config)
        self.config.update(json_config)
        env_config = self.load_env_config()
        self.config.update(env_config)
        arg_config = self.load_arg_config(args)
        self.config.update(arg_config)

        self.host_arch = platform.machine()
        self.is_arm = self.host_arch.startswith('arm')

        self.cleanup_config()

        if self.config['dirty'] and 'clean' in self.config['default']:
            self.config['default'].remove('clean')
        self.config['default'] = ' '.join(self.config['default'])

        self.build_arch = self.config['arch']
        if self.config['template'] == self.PURE_QML_QMAKE or self.config['template'] == self.PURE_QML_CMAKE or self.config['template'] == self.PURE:
            self.build_arch = 'armhf'

        if self.config['arch'] == 'all':
            self.build_arch = 'armhf'

        if self.desktop:
            self.build_arch = 'amd64'

        if not self.config['docker_image']:
            self.custom_docker_image = False
            image = self.build_arch
            if self.use_nvidia:
                image = "{}-nvidia".format(image)
            if self.is_xenial:
                self.config['docker_image'] = self.container_mapping[('16.04', image)]
            else:
                self.config['docker_image'] = self.container_mapping[('15.04', image)]

        self.config['arch_triplet'] = self.arch_triplet_mapping[self.config['arch']]

        for key in self.path_keys:
            if key not in self.accepts_placeholders and self.config[key]:
                self.config[key] = os.path.abspath(self.config[key])

        self.substitute_placeholders()

        self.check_config_errors()

        self.lib_configs = [LibConfig(name, lib, self.config['arch'], self.config['root_dir'], self.debug_build)
                                    for name, lib in self.config['libraries'].items()]

    def __getattr__(self, name):
        return self.config[name]

    def __setattr__(self, name, value):
        if name in self.config:
            self.config[name] = value
        else:
            super().__setattr__(name, value)

    def load_json_schema(self):
        schema_path = os.path.join(os.path.dirname(__file__), 'clickable.schema')
        with open(schema_path, 'r') as f:
            schema = {}
            try:
                return json.load(f)
            except ValueError:
                raise ValueError('Failed reading "clickable.schema", it is not valid json')
            return None

    def load_json_config(self, config_path):
        config = {}
        use_default_config = not config_path
        if use_default_config:
            config_path = os.path.join(self.cwd, 'clickable.json')

        if os.path.isfile(config_path):
            with open(config_path, 'r') as f:
                config_json = {}
                try:
                    config_json = json.load(f)
                except ValueError:
                    raise ValueError('Failed reading "clickable.json", it is not valid json')

                for key in self.deprecated:
                    if key in config_json:
                        raise ValueError('"{}" is a no longer a valid configuration option'.format(key))

                schema = self.load_json_schema()
                validate_clickable_json(config=config_json, schema=schema)

                for key in self.config:
                    value = config_json.get(key, None)

                    if value:
                        config[key] = value
        elif not use_default_config:
            raise ValueError('Specified config file {} does not exist.'.format(config_path))

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
            self.use_nvidia = True

        if args.apikey:
            self.apikey = args.apikey

        if args.vivid:
            self.is_xenial = not args.vivid

        if args.debug:
            self.debug = True

        if args.debug_build:
            self.debug_build = True

        if args.gdb:
            self.debug_build = True
            self.debug_gdb = True

        if args.gdbserver:
            self.debug_build = True
            self.debug_gdb = True
            self.debug_gdb_port = args.gdbserver

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

    def substitute_placeholders(self):
        for key in self.accepts_placeholders:
            for sub in self.replacements:
                rep = self.config[self.replacements[sub]]
                if self.config[key]:
                    if isinstance(self.config[key], dict):
                        self.config[key] = {k: val.replace(sub, rep) for (k, val) in self.config[key].items()}
                    elif isinstance(self.config[key], list):
                        self.config[key] = [val.replace(sub, rep) for val in self.config[key]]
                    else:
                        self.config[key] = self.config[key].replace(sub, rep)
            if key in self.path_keys and self.config[key]:
                self.config[key] = os.path.abspath(self.config[key])

    def convert_deprecated_libraries_list(self):
        if isinstance(self.config['libraries'], list):
            print_warning("Specifying libraries as a list is deprecated and will be removed in a future version of Clickable. Specify the libraries as a dictionary instead.")

            dict_libs = {}
            for lib in self.config['libraries']:
                if not 'name' in lib:
                    raise ValueError("Library without name detected")
                dict_libs[lib['name']] = lib
            self.config['libraries'] = dict_libs

    def cleanup_config(self):
        self.make_args = merge_make_jobs_into_args(make_args=self.make_args, make_jobs=self.make_jobs)

        if self.config['dir']:
            self.config['build_dir'] = self.config['dir']
            print_warning('The param "dir" in your clickable.json is deprecated and will be removed in a future version of Clickable. Use "build_dir" instead!')

        self.convert_deprecated_libraries_list()

        for key in self.flexible_lists:
            self.config[key] = flexible_string_to_list(self.config[key])

        if self.desktop:
            self.config['arch'] = 'amd64'
        elif self.config['template'] == self.PURE_QML_CMAKE or self.config['template'] == self.PURE_QML_QMAKE or self.config['template'] == self.PURE:
            self.config['arch'] = 'all'

        if not self.config['kill']:
            if self.config['template'] == self.CORDOVA:
                self.config['kill'] = 'cordova-ubuntu'
            elif self.config['template'] == self.PURE_QML_CMAKE or self.config['template'] == self.PURE_QML_QMAKE or self.config['template'] == self.PURE:
                self.config['kill'] = 'qmlscene'
            else:
                try:
                    desktop = get_desktop(self.cwd)
                except ValueError:
                    desktop = None
                except FileNotFoundException:
                    desktop = None

                if desktop and 'Exec' in desktop:
                    self.config['kill'] = desktop['Exec'].replace('%u', '').replace('%U', '').strip()

        if self.config['dependencies']:
            if self.config['specificDependencies']:
                self.config['dependencies_build'] += self.config['dependencies']
            else:
                self.config['dependencies_target'] += self.config['dependencies']
            print_warning('The params "dependencies" (and possibly "specificDependencies") in your clickable.json are deprecated and will be removed in a future version of Clickable. Use "dependencies_build" and "dependencies_target" instead!')

        if self.desktop:
            self.config['dependencies_build'] += self.config['dependencies_target']
            self.config['dependencies_target'] = []

        self.ignore.extend(['.git', '.bzr'])

    def check_config_errors(self):
        if self.debug_gdb and not self.desktop:
            raise ValueError("GDB debugging is only supported in desktop mode! Consider running 'clickable desktop --gdb'")

        if self.config['clickable_minimum_required']:
            # Check if specified version string is valid
            if not re.fullmatch("\d+(\.\d+)*", self.config['clickable_minimum_required']):
                raise ValueError('"{}" specified as "clickable_minimum_required" is not a valid version number'.format(self.config['clickable_minimum_required']))

            # Convert version strings to integer lists
            clickable_version_numbers = [int(n) for n in re.split('\.', self.clickable_version)]
            clickable_required_numbers = [int(n) for n in re.split('\.', self.config['clickable_minimum_required'])]
            if len(clickable_required_numbers) > len(clickable_version_numbers):
                print_warning('Clickable version number only consists of {} numbers, but {} numbers specified in "clickable_minimum_required". Superfluous numbers will be ignored.'.format(len(clickable_version_numbers), len(clickable_required_numbers)))

            # Compare all numbers until finding an unequal pair
            for req, ver in zip(clickable_required_numbers, clickable_version_numbers):
                if req < ver:
                    break
                if req > ver:
                    raise ValueError('This project requires Clickable version {} ({} is used). Please update Clickable!'.format(self.config['clickable_minimum_required'], self.clickable_version))

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
                except FileNotFoundException:
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
        return find_manifest(self.cwd, self.install_dir, self.config['build_dir'], ignore_dir)

    def get_manifest(self):
        return get_manifest(self.cwd, self.install_dir, self.config['build_dir'])

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
