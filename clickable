#!/usr/bin/env python2

import argparse
import itertools
import subprocess
import shlex
import os
import sys
import json
import shutil
import platform
import xml.etree.ElementTree as ElementTree

# TODO generate clickable.json file
# TODO add Golang template
# TODO add desktop arch
# TODO make a snap
# TODO lxd setup shouldn't require a clickable.json
# TODO check for a template based on CMake files, etc


class Colors:
    INFO = '\033[94m'
    SUCCESS = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    CLEAR = '\033[0m'


def print_info(message):
    print(Colors.INFO + message + Colors.CLEAR)


def print_success(message):
    print(Colors.SUCCESS + message + Colors.CLEAR)


def print_warning(message):
    print(Colors.WARNING + message + Colors.CLEAR)


def print_error(message):
    print(Colors.ERROR + message + Colors.CLEAR)


def find_manifest(cwd, temp_dir=None, build_dir=None):
    manifests = []
    searchpaths = []
    searchpaths.append(cwd)

    if build_dir and not build_dir.startswith(os.path.realpath(cwd) + os.sep):
        searchpaths.append(build_dir)

    for (root, dirs, files) in itertools.chain.from_iterable(os.walk(path, topdown=True) for path in searchpaths):
        for name in files:
            if name == 'manifest.json':
                manifests.append(os.path.join(root, name))

    if not manifests:
        raise Exception('Could not find manifest.json')

    # Favor the manifest in the install dir first, then fall back to the build dir and finally the source dir
    manifest = ''
    for m in manifests:
        if temp_dir and m.startswith(os.path.realpath(temp_dir) + os.sep):
            manifest = m

    if not manifest:
        for m in manifests:
            if build_dir and m.startswith(os.path.realpath(build_dir) + os.sep):
                manifest = m

    if not manifest:
        manifest = manifests[0]

    return manifest


def get_manifest(cwd, temp_dir=None, build_dir=None):
    manifest = {}
    with open(find_manifest(cwd, temp_dir, build_dir), 'r') as f:
        try:
            manifest = json.load(f)
        except ValueError:
            raise ValueError('Failed reading "manifest.json", it is not valid json')

    return manifest


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
        'default': 'kill clean build click-build install launch',
        'log': None,
        'specificDependencies': False,  # TODO make this less confusing
        'dependencies': [],  # TODO support this being a string
        'ignore': [],
        'make_jobs': 0,
    }

    PURE_QML_QMAKE = 'pure-qml-qmake'
    QMAKE = 'qmake'
    PURE_QML_CMAKE = 'pure-qml-cmake'
    CMAKE = 'cmake'
    CUSTOM = 'custom'
    CORDOVA = 'cordova'
    PURE = 'pure'
    PYTHON = 'python'

    required = ['sdk', 'arch', 'dir']
    templates = [PURE_QML_QMAKE, QMAKE, PURE_QML_CMAKE, CMAKE, CUSTOM, CORDOVA, PURE, PYTHON]

    def __init__(self, ip=None, arch=None, template=None, skip_detection=False):
        self.cwd = os.getcwd()
        self.load_config()

        if ip:
            self.ssh = ip

        if arch:
            self.arch = arch

        if template:
            self.template = template

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
                self.kill = self.app

        if self.template == self.PURE_QML_CMAKE or self.template == self.PURE_QML_QMAKE or self.template == self.PURE:
            self.arch = 'all'

        if self.template == self.CUSTOM and not self.build:
            raise ValueError('When using the "custom" template you must specify a "build" in the config')

        if self.template not in self.templates:
            raise ValueError('"{}" is not a valid template ({})'.format(self.template, ', '.join(self.templates)))

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


class Clickable(object):
    cwd = None
    usdk_target = 'usdk-target'

    def __init__(self, config, device_serial_number=None):
        self.cwd = os.getcwd()
        self.config = config
        self.temp = os.path.join(self.config.dir,'tmp')
        self.device_serial_number = device_serial_number
        if type(self.device_serial_number) == type([]) and len(self.device_serial_number) > 0:
            self.device_serial_number = self.device_serial_number[0]

        self.host_arch = 'amd64' if platform.architecture()[0] == '64bit' else 'i386'
        self.build_arch = self.config.arch
        if self.config.template == self.config.PURE_QML_QMAKE or self.config.template == self.config.PURE_QML_CMAKE or self.config.template == self.config.PURE:
            self.build_arch = 'armhf'

        if self.config.ssh:
            self.check_command('ssh')
            self.check_command('scp')
        else:
            self.check_command('adb')

        if self.config.chroot:
            self.check_command('click')

        if self.config.template == Config.CORDOVA:
            self.check_command('cordova')

        if 'SNAP' in os.environ and os.environ['SNAP']:
            # If running as a snap, trick usdk-target into thinking its not in a snap
            del os.environ['SNAP']

        usdk_target_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'usdk-target')
        if os.path.isfile(usdk_target_path):
            self.usdk_target = usdk_target_path
        else:
            try:
                self.check_command('usdk-target')
            except Exception:
                raise Exception('The command "usdk-target" does not exist on this system, you can find it in the clickable repo')

            print_warning('Using the system version of usdk-target and not clickable\'s')

    def check_command(self, command):
        error_code = subprocess.call(shlex.split('which {}'.format(command)), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if error_code != 0:
            raise Exception('The command "{}" does not exist on this system, please install it for clickable to work properly"'.format(command))

    def find_manifest(self):
        return find_manifest(self.cwd, self.temp, self.config.dir)

    def get_manifest(self):
        return get_manifest(self.cwd, self.temp, self.config.dir)

    def find_version(self):
        return self.get_manifest().get('version', '1.0')

    def find_package_name(self):
        package = self.config.package

        if not package:
            package = self.get_manifest().get('name', None)

        if not package:
            raise ValueError('No package name specified in manifest.json or clickable.json')

        return package

    def find_app_name(self):
        app = self.config.app

        if not app:
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

    def run_device_command(self, command, cwd=None):
        if not cwd:
            cwd = self.config.dir

        wrapped_command = ''
        if self.config.ssh:
            wrapped_command = 'echo "{}" | ssh phablet@{}'.format(command, self.config.ssh)
        else:
            if self.device_serial_number:
                wrapped_command = 'adb -s {} shell "{}"'.format(self.device_serial_number, command)
            else:
                wrapped_command = 'adb shell "{}"'.format(command)

        subprocess.check_call(wrapped_command, cwd=cwd, shell=True)

    def run_container_command(self, command, force_lxd=False, sudo=False, get_output=False, use_dir=True):
        wrapped_command = command
        if self.config.chroot and not force_lxd:
            chroot_command = 'run'
            if sudo:
                chroot_command = 'maint'

            wrapped_command = 'click chroot -a {} -f {} {} {}'.format(self.build_arch, self.config.sdk, chroot_command, command)
        else:
            self.check_lxd()

            target_command = 'exec'
            if sudo:
                target_command = 'maint'

            if use_dir:
                command = 'cd {}; {}'.format(self.config.dir, command)

            wrapped_command = '{} {} clickable-{} -- bash -c "{}"'.format(self.usdk_target, target_command, self.build_arch, command)

        kwargs = {}
        if use_dir:
            kwargs['cwd'] = self.config.dir

        if get_output:
            return subprocess.check_output(shlex.split(wrapped_command), **kwargs)
        else:
            subprocess.check_call(shlex.split(wrapped_command), **kwargs)

    def setup_dependencies(self):
        if len(self.config.dependencies) > 0:
            print_info('Checking dependencies')

            command = 'apt-get install -y --force-yes'
            run = False
            for dep in self.config.dependencies:
                if self.config.arch == 'armhf' and 'armhf' not in dep and not config.specificDependencies:
                    dep = '{}:{}'.format(dep, self.config.arch)

                exists = ''
                try:
                    exists = self.run_container_command('dpkg -s {} | grep Status'.format(dep), get_output=True, use_dir=False)
                except subprocess.CalledProcessError:
                    exists = ''

                if exists.strip() != 'Status: install ok installed':
                    run = True
                    command = '{} {}'.format(command, dep)

            if run:
                self.run_container_command(command, sudo=True, use_dir=False)
            else:
                print_info('Dependencies already installed')

    def check_lxd(self):
        name = 'clickable-{}'.format(self.build_arch)

        status = ''
        try:
            status = subprocess.check_output(shlex.split('{} status {}'.format(self.usdk_target, name)), stderr=subprocess.STDOUT)
            status = json.loads(status)['status']
        except subprocess.CalledProcessError as e:
            if e.output.strip() == 'error: Could not connect to the LXD server.':
                # TODO explain how to start lxd and/or try to start it
                raise Exception('LXD is not running, please start it')
            elif e.output.strip() == 'error: Could not query container status. error: not found':
                raise Exception('No lxd container exists to build in, please run `clickable setup-lxd`')
            else:
                print(e.output)
                raise e

        if status != 'Running':
            print_info('Going to start lxd container "{}"'.format(name))
            subprocess.check_call(shlex.split('lxc start {}'.format(name)))

    def lxd_container_exists(self):
        name = 'clickable-{}'.format(self.build_arch)

        # Check for existing container
        existing = subprocess.check_output(shlex.split('{} list'.format(self.usdk_target)))
        existing = json.loads(existing)

        found = False
        for container in existing:
            if container['name'] == name:
                found = True

        return found

    def setup_lxd(self):
        name = 'clickable-{}'.format(self.build_arch)
        alias = '{}-{}-{}-dev'.format(self.config.sdk, self.host_arch, self.build_arch)

        if self.lxd_container_exists():
            print_success('Container already exists, nothing to do')
        else:
            print_info('Going to setup the lxd container')

            # Find the image we want
            images = subprocess.check_output(shlex.split('{} images'.format(self.usdk_target)))
            images = json.loads(images)

            fingerprint = None
            for image in images:
                if image['alias'] == alias:
                    fingerprint = image['fingerprint']

            if not fingerprint:
                raise Exception('The {} lxd image could not be found'.format(alias))

            print_info('Asking for root to create the lxd container')

            # If set, pass along the USDK_TEST_REMOTE env var (this allows user to use a different sdk image server)
            env = ''
            if 'USDK_TEST_REMOTE' in os.environ:
                env = 'USDK_TEST_REMOTE={}'.format(os.environ['USDK_TEST_REMOTE'])

            # Create a new container
            subprocess.check_call(shlex.split('sudo {} {} create -n {} -p {}'.format(env, self.usdk_target, name, fingerprint)))

            self.run_container_command('apt-get update', force_lxd=True, sudo=True, use_dir=False)
            self.run_container_command('apt-get install -y --force-yes click', force_lxd=True, sudo=True, use_dir=False)

            print_success('Finished setting up the lxd container')

    def click_build(self):
        command = 'click build {} --no-validate'.format(os.path.dirname(self.find_manifest()))

        if self.config.chroot:
            subprocess.check_call(shlex.split(command), cwd=self.config.dir)
        else:
            # Run this in the container so the host doesn't need to have click installed
            self.run_container_command(command)

        self.click_review()

    def click_review(self):
        pass  # TODO implement this

    def install(self, click_path=None):
        cwd = '.'
        if click_path:
            click = os.path.basename(click_path)
        else:
            click = '{}_{}_{}.click'.format(self.find_package_name(), self.find_version(), self.config.arch)
            click_path = os.path.join(self.config.dir, click)
            cwd = self.config.dir

        if self.config.ssh:
            command = 'scp {} phablet@{}:/home/phablet/'.format(click_path, self.config.ssh)
            subprocess.check_call(command, cwd=cwd, shell=True)

        else:
            if self.device_serial_number:
                command = 'adb -s {} push {} /home/phablet/'.format(self.device_serial_number, click_path)
            else:
                command = 'adb push {} /home/phablet/'.format(click_path)
            subprocess.check_call(command, cwd=cwd, shell=True)

        self.run_device_command('pkcon install-local --allow-untrusted {}'.format(click), cwd=cwd)

    def kill(self):
        if self.config.kill:
            try:
                self.run_device_command('pkill -f {}'.format(self.config.kill))
            except:
                pass  # Nothing to do, the process probably wasn't running

    def launch(self, app=None):
        cwd = '.'
        if not app:
            app = '{}_{}_{}'.format(self.find_package_name(), self.find_app_name(), self.find_version())
            cwd = self.config.dir

        launch = 'ubuntu-app-launch {}'.format(app)
        if self.config.launch:
            launch = self.config.launch

        self.run_device_command('sleep 1s && {}'.format(launch), cwd=cwd)

    def logs(self):
        # TODO Support scope logs
        log = '~/.cache/upstart/application-click-{}_{}_{}.log'.format(self.find_package_name(), self.find_app_name(), self.find_version())

        if self.config.log:
            log = self.config.log

        self.run_device_command('tail -f {}'.format(log))

    def clean(self):
        try:
            shutil.rmtree(self.config.dir)
        except:
            type, value, traceback = sys.exc_info()
            if type == OSError and 'No such file or directory' in value:  # TODO see if there is a proper way to do this
                pass  # Nothing to do here, the directory didn't exist
            else:
                print_warning('Failed to clean the build directory: {}: {}'.format(type, value))

        try:
            shutil.rmtree(self.temp)
        except:
            type, value, traceback = sys.exc_info()
            if type == OSError and 'No such file or directory' in value:  # TODO see if there is a proper way to do this
                pass  # Nothing to do here, the directory didn't exist
            else:
                print_warning('Failed to clean the temp directory: {}: {}'.format(type, value))

    def _build(self):
        raise NotImplementedError()

    def build(self):
        try:
            os.makedirs(self.config.dir)
        except:
            print_warning('Failed to create the build directory: {}'.format(str(sys.exc_info()[0])))

        self.setup_dependencies()

        if self.config.prebuild:
            subprocess.check_call(self.config.prebuild, cwd=self.cwd, shell=True)

        self._build()

        if self.config.postbuild:
            subprocess.check_call(self.config.postbuild, cwd=self.config.dir, shell=True)

    def script(self, name, device=False):
        if name in self.config.scripts:
            if device:
                self.run_device_command('{}'.format(self.config.scripts[name]))
            else:
                subprocess.check_call(self.config.scripts[name], cwd=self.cwd, shell=True)


class MakeClickable(Clickable):
    def pre_make(self):
        if self.config.premake:
            subprocess.check_call(self.config.premake, cwd=self.config.dir, shell=True)

    def post_make(self):
        if self.config.postmake:
            subprocess.check_call(self.config.premake, cwd=self.config.dir, shell=True)

    def make(self):
        command = 'make -j'
        if self.config.make_jobs:
            command = '{}{}'.format(command, self.config.make_jobs)

        self.run_container_command(command)

    def make_install(self):
        if os.path.exists(self.temp) and os.path.isdir(self.temp):
            shutil.rmtree(self.temp)

        try:
            os.makedirs(self.temp)
        except:
            print_warning('Failed to create temp dir ({}): {}'.format(self.temp, str(sys.exc_info()[0])))

        # The actual make command is implemented in the subclasses

    def _build(self):
        self.pre_make()
        self.make()
        self.post_make()
        self.make_install()


class CMakeClickable(MakeClickable):
    def make_install(self):
        super(CMakeClickable, self).make_install()

        self.run_container_command('make DESTDIR={} install'.format(self.temp))

    def _build(self):
        self.run_container_command('cmake {}'.format(self.cwd))

        super(CMakeClickable, self)._build()


class QMakeClickable(MakeClickable):
    def make_install(self):
        super(QMakeClickable, self).make_install()

        self.run_container_command('make INSTALL_ROOT={} install'.format(self.temp))

    def _build(self):
        if self.build_arch == 'armhf':
            self.run_container_command('qt5-qmake-arm-linux-gnueabihf {}'.format(self.cwd))
        else:
            raise Exception('{} is not supported by the qmake build yet'.format(self.build_arch))

        super(QMakeClickable, self)._build()


class CustomClickable(Clickable):
    def _build(self):
        self.run_container_command(self.config.build)


class PureQMLMakeClickable(MakeClickable):
    def post_make(self):
        super(PureQMLMakeClickable, self).post_make()

        with open(self.find_manifest(), 'r') as f:
            manifest = {}
            try:
                manifest = json.load(f)
            except ValueError:
                raise ValueError('Failed reading "manifest.json", it is not valid json')

            manifest['architecture'] = 'all'
            with open(self.find_manifest(), 'w') as writer:
                json.dump(manifest, writer, indent=4)


class PureQMLQMakeClickable(PureQMLMakeClickable, QMakeClickable):
    pass


class PureQMLCMakeClickable(PureQMLMakeClickable, CMakeClickable):
    pass


class PureClickable(Clickable):
    def _ignore(self, path, contents):
        ignored = []
        for content in contents:
            cpath = os.path.abspath(os.path.join(path, content))
            if cpath == os.path.abspath(self.temp) or cpath == os.path.abspath(self.config.dir) or content in self.config.ignore or content == 'clickable.json':
                ignored.append(content)

        return ignored

    def _build(self):
        shutil.copytree(self.cwd, self.temp, ignore=self._ignore)
        print_info('Copied files to temp directory for click building')


class PythonClickable(PureClickable):
    # The only difference between this and the Pure template is that this doesn't force the "all" arch
    pass


class CordovaClickable(Clickable):
    def _build(self):
        command = "cordova -d build ubuntu --device -- --framework={}".format(self.config.sdk)
        subprocess.check_call(shlex.split(command), cwd=self.cwd)

    def click_build(self):
        click = '{}_{}_{}.click'.format(self.find_package_name(), self.find_version(), self.config.arch)
        src = '{}/platforms/ubuntu/{}/{}/prefix/{}'.format(self.cwd, self.config.sdk, self.config.arch, click)
        dest = '{}/{}'.format(self.config.dir, click)

        shutil.copyfile(src, dest)

    def find_package_name(self):
        tree = ElementTree.parse('config.xml')
        root = tree.getroot()
        return root.attrib['id'] if 'id' in root.attrib else '1.0.0'

    def find_version(self):
        tree = ElementTree.parse('config.xml')
        root = tree.getroot()
        return root.attrib['version'] if 'version' in root.attrib else '1.0.0'


if __name__ == "__main__":
    config = None
    COMMAND_HANDLERS = {
        "kill": "kill",
        "clean": "clean",
        "build": "build",
        "click_build": "click_build",
        "click-build": "click_build",
        "build_click": "click_build",
        "build-click": "click_build",
        "install": "install",
        "launch": "launch",
        "logs": "logs",
        "setup-lxd": "setup_lxd"
    }

    def show_valid_commands():
        n = [
            'Valid commands:',
            ", ".join(sorted(COMMAND_HANDLERS.keys()))
        ]
        if config and hasattr(config, "scripts") and config.scripts:
            n += [
                'Project-specific custom commands:',
                ", ".join(sorted(config.scripts.keys()))
            ]
        return "\n".join(n)

    def print_valid_commands():
            print(show_valid_commands())

    # TODO better help text & version
    parser = argparse.ArgumentParser(description='clickable')
    parser.add_argument('commands', nargs='*', help=show_valid_commands())
    parser.add_argument('--device', '-d', action="store_true", default=False)
    parser.add_argument(
        '--device-serial-number',
        '-s',
        help='Directs command to the device or emulator with the given serial number or qualifier (using adb)',
        default=None
    )
    parser.add_argument(
        '--ip',
        '-i',
        help='Directs command to the device with the given IP address (using ssh)'
    )
    parser.add_argument(
        '--arch',
        '-a',
        help='Use the specified arch when building (ignores the setting in clickable.json)'
    )
    parser.add_argument(
        '--template',
        '-t',
        help='Use the specified template when building (ignores the setting in clickable.json)'
    )
    parser.add_argument(
        '--click',
        '-c',
        help='Installs the specified click (use with the "install" command)'
    )
    parser.add_argument(
        '--app',
        '-p',
        help='Launches the specified app (use with the "launch" command)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Runs in debug mode'
    )
    args = parser.parse_args()

    skip_detection = False
    if args.click:
        skip_detection = True
    elif 'setup-lxd' in args.commands:
        skip_detection = True

    try:
        config = Config(ip=args.ip, arch=args.arch, template=args.template, skip_detection=skip_detection)
        clickable = None
        if config.template == config.PURE_QML_QMAKE:
            clickable = PureQMLQMakeClickable(config, args.device_serial_number)
        elif config.template == config.QMAKE:
            clickable = QMakeClickable(config, args.device_serial_number)
        elif config.template == config.PURE_QML_CMAKE:
            clickable = PureQMLCMakeClickable(config, args.device_serial_number)
        elif config.template == config.CMAKE:
            clickable = CMakeClickable(config, args.device_serial_number)
        elif config.template == config.CUSTOM:
            clickable = CustomClickable(config, args.device_serial_number)
        elif config.template == config.CORDOVA:
            clickable = CordovaClickable(config, args.device_serial_number)
        elif config.template == config.PURE:
            clickable = PureClickable(config, args.device_serial_number)
        elif config.template == config.PYTHON:
            clickable = PythonClickable(config, args.device_serial_number)

        commands = args.commands
        if len(args.commands) == 0:
            commands = config.default.split(' ')

        for command in commands:
            if command in config.scripts:
                clickable.script(command, args.device)
            elif command == 'install':
                clickable.install(args.click)
            elif command == 'launch':
                clickable.launch(args.app)
            elif command in COMMAND_HANDLERS:
                getattr(clickable, COMMAND_HANDLERS[command])()
            elif command == 'help':
                parser.print_help()
            else:
                print_error('There is no builtin or custom command named "{}"'.format(command))
                print_valid_commands()
    except:
        if args.debug:
            raise
        else:
            print_error(str(sys.exc_info()[1]))
