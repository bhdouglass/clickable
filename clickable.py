#!/usr/bin/env python3

import argparse
import itertools
import subprocess
import shlex
import os
import sys
import json
import shutil
import time
import uuid
import xml.etree.ElementTree as ElementTree
import getpass

from distutils.dir_util import copy_tree

cookiecutter_available = True
try:
    from cookiecutter.main import cookiecutter
except ImportError:
    cookiecutter_available = False

# TODO include phablet-config
# TODO add a publish command to upload to the OpenStore
# TODO create a flatpak
# TODO split into multiple files


__version__ = '4.2.0'


def run_subprocess_call(cmd, **args):
    if isinstance(cmd, str):
        cmd = cmd.encode()
    elif isinstance(cmd, (list, tuple)):
        for idx, x in enumerate(cmd):
            if isinstance(x, str):
                cmd[idx] = x.encode()
    return subprocess.call(cmd, **args)


def run_subprocess_check_output(cmd, **args):
    if isinstance(cmd, str):
        cmd = cmd.encode()
    elif isinstance(cmd, (list, tuple)):
        for idx, x in enumerate(cmd):
            if isinstance(x, str):
                cmd[idx] = x.encode()
    return subprocess.check_output(cmd, **args).decode()


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


class ManifestNotFoundException(Exception):
    pass


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
        raise ManifestNotFoundException('Could not find manifest.json')

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
        self.container_mode = container_mode
        self.desktop = desktop
        self.use_nvidia = use_nvidia
        self.cwd = os.getcwd()
        self.load_config()

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


class Clickable(object):
    cwd = None

    def __init__(self, config, device_serial_number=None, click_output=None):
        self.cwd = os.getcwd()
        self.config = config
        self.temp = os.path.join(self.config.dir, 'tmp')
        self.device_serial_number = device_serial_number
        if type(self.device_serial_number) == list and len(self.device_serial_number) > 0:
            self.device_serial_number = self.device_serial_number[0]

        self.build_arch = self.config.arch
        if self.config.template == self.config.PURE_QML_QMAKE or self.config.template == self.config.PURE_QML_CMAKE or self.config.template == self.config.PURE:
            self.build_arch = 'armhf'
            if self.config.desktop:
                self.build_arch = 'amd64'

        if self.config.arch == 'all':
            self.build_arch = 'armhf'
            if self.config.desktop:
                self.build_arch = 'amd64'

        if not self.config.container_mode:
            if self.config.ssh:
                self.check_command('ssh')
                self.check_command('scp')
            else:
                self.check_command('adb')

        if 'SNAP' in os.environ and os.environ['SNAP']:
            # If running as a snap, trick usdk-target into thinking its not in a snap
            del os.environ['SNAP']

        if not self.config.container_mode:
            if self.config.chroot:
                print_warning('Use of chroots are depricated and will be removed in a future version')
                self.check_command('click')
            elif self.config.lxd:
                print_warning('Use of lxd is depricated and will be removed in a future version')
                self.check_command('usdk-target')
            else:
                self.check_command('docker')
                self.docker_image = 'clickable/ubuntu-sdk:{}-{}'.format(self.config.sdk.replace('ubuntu-sdk-', ''), self.build_arch)
                if self.config.use_nvidia:
                    self.docker_image += '-nvidia'
                    self.check_command('nvidia-docker')

                self.base_docker_image = self.docker_image

                if os.path.exists('.clickable/name.txt'):
                    with open('.clickable/name.txt', 'r') as f:
                        self.docker_image = f.read().strip()

    def check_command(self, command):
        error_code = run_subprocess_call(shlex.split('which {}'.format(command)), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

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
        if self.config.container_mode:
            print_warning('Skipping device command, running in container mode')
            return

        if not cwd:
            cwd = self.config.dir

        wrapped_command = ''
        if self.config.ssh:
            wrapped_command = 'echo "{}" | ssh phablet@{}'.format(command, self.config.ssh)
        else:
            if self.device_serial_number:
                wrapped_command = 'adb -s {} shell "{}"'.format(self.device_serial_number, command)
            else:
                self.check_multiple_devices()
                wrapped_command = 'adb shell "{}"'.format(command)

        subprocess.check_call(wrapped_command, cwd=cwd, shell=True)

    def run_container_command(self, command, force_lxd=False, sudo=False, get_output=False, use_dir=True):
        wrapped_command = command

        if self.config.container_mode:
            wrapped_command = 'bash -c "{}"'.format(command)
        elif force_lxd or self.config.lxd:
            self.check_lxd()

            target_command = 'exec'
            if sudo:
                target_command = 'maint'

            if use_dir:
                command = 'cd {}; {}'.format(self.config.dir, command)

            wrapped_command = 'usdk-target {} clickable-{} -- bash -c "{}"'.format(target_command, self.build_arch, command)
        elif self.config.chroot:
            chroot_command = 'run'
            if sudo:
                chroot_command = 'maint'

            wrapped_command = 'click chroot -a {} -f {} {} bash -c "{}"'.format(self.build_arch, self.config.sdk, chroot_command, command)
        else:  # Docker
            self.check_docker()

            go_config = ''
            if self.config.gopath:
                go_config = '-v {}:/gopath -e GOPATH=/gopath'.format(self.config.gopath)

            wrapped_command = 'docker run -v {}:{} {} -w {} -u {} --rm -i {} bash -c "{}"'.format(
                self.cwd,
                self.cwd,
                go_config,
                self.config.dir if use_dir else self.cwd,
                os.getuid(),
                self.docker_image,
                command,
            )

        kwargs = {}
        if use_dir:
            kwargs['cwd'] = self.config.dir

        if get_output:
            return run_subprocess_check_output(shlex.split(wrapped_command), **kwargs)
        else:
            subprocess.check_call(shlex.split(wrapped_command), **kwargs)

    def setup_dependencies(self):
        if len(self.config.dependencies) > 0:
            print_info('Checking dependencies')

            if self.config.lxd or self.config.chroot or self.config.container_mode:
                command = 'apt-get install -y --force-yes'
                run = False
                for dep in self.config.dependencies:
                    if self.config.arch == 'armhf' and 'armhf' not in dep and not self.config.specificDependencies:
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
            else:  # Docker
                self.check_docker()

                dependencies = ''
                for dep in self.config.dependencies:
                    if self.config.arch == 'armhf' and 'armhf' not in dep and not self.config.specificDependencies:
                        dependencies = '{} {}:{}'.format(dependencies, dep, self.config.arch)
                    else:
                        dependencies = '{} {}'.format(dependencies, dep)

                dockerfile = '''
FROM {}
RUN echo set debconf/frontend Noninteractive | debconf-communicate && echo set debconf/priority critical | debconf-communicate
RUN apt-get update && apt-get install -y --force-yes --no-install-recommends {} && apt-get clean
                '''.format(
                    self.base_docker_image,
                    dependencies
                ).strip()

                build = False

                if not os.path.exists('.clickable'):
                    os.makedirs('.clickable')

                if os.path.exists('.clickable/Dockerfile'):
                    with open('.clickable/Dockerfile', 'r') as f:
                        if dockerfile.strip() != f.read().strip():
                            build = True
                else:
                    build = True

                if build:
                    with open('.clickable/Dockerfile', 'w') as f:
                        f.write(dockerfile)

                    self.docker_image = '{}-{}'.format(self.base_docker_image, uuid.uuid4())
                    with open('.clickable/name.txt', 'w') as f:
                        f.write(self.docker_image)

                    print_info('Generating new docker image')
                    subprocess.check_call(shlex.split('docker build -t {} .'.format(self.docker_image)), cwd='.clickable')
                else:
                    print_info('Dependencies already setup')

    def start_docker(self):
        started = False
        error_code = run_subprocess_call(shlex.split('which systemctl'), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if error_code == 0:
            print_info('Asking for root to start docker')
            error_code = run_subprocess_call(shlex.split('sudo systemctl start docker'))

            started = (error_code == 0)

        return started

    def check_docker(self, retries=3):
        try:
            run_subprocess_check_output(shlex.split('docker ps'), stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            retries -= 1
            if retries <= 0:
                raise e

            self.start_docker()

            time.sleep(3)  # Give it a sec to boot up
            self.check_docker(retries)

    def start_lxd(self):
        started = False
        error_code = run_subprocess_call(shlex.split('which systemctl'), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if error_code == 0:
            print_info('Asking for root to start lxd')
            error_code = run_subprocess_call(shlex.split('sudo systemctl start lxd'))

            started = (error_code == 0)

        return started

    def check_lxd(self):
        name = 'clickable-{}'.format(self.build_arch)

        status = ''
        try:
            status = run_subprocess_check_output(shlex.split('usdk-target status {}'.format(name)), stderr=subprocess.STDOUT)
            status = json.loads(status)['status']
        except subprocess.CalledProcessError as e:
            if e.output.strip() == 'error: Could not connect to the LXD server.' or 'Can\'t establish a working socket connection' in e.output.strip():
                started = self.start_lxd()
                if started:
                    status = 'Running'  # Pretend it's started, but we will call this function again to check if it's actually ok

                    time.sleep(3)  # Give it a sec to boot up
                    self.check_lxd()
                else:
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
        existing = run_subprocess_check_output(shlex.split('{} list'.format(self.usdk_target)))
        existing = json.loads(existing)

        found = False
        for container in existing:
            if container['name'] == name:
                found = True

        return found

    def setup_lxd(self):
        print_error('Setting up lxd is no longer supported, use docker instead')

    def setup_docker(self):
        self.check_command('docker')
        self.start_docker()

        group_exists = False
        with open('/etc/group', 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith('docker:'):
                    group_exists = True

        if not group_exists:
            print_info('Asking for root to create docker group')
            subprocess.check_call(shlex.split('sudo groupadd docker'))

        output = run_subprocess_check_output(shlex.split('groups {}'.format(getpass.getuser()))).strip()
        # Test for exactly docker in the group list
        if ' docker ' in output or output.endswith(' docker') or output.startswith('docker ') or output == 'docker':
            print_info('Setup has already been completed')
        else:
            print_info('Asking for root to add the current user to the docker group')
            subprocess.check_call(shlex.split('sudo usermod -aG docker {}'.format(getpass.getuser())))

            print_info('Log out or restart to apply changes')

    def display_on(self):
        command = 'powerd-cli display on'
        self.run_device_command(command, cwd=self.cwd)

    def no_lock(self):
        print_info('Turning off device activity timeout')
        command = 'gsettings set com.ubuntu.touch.system activity-timeout 0'
        self.run_device_command(command, cwd=self.cwd)

    def click_build(self):
        command = 'click build {} --no-validate'.format(os.path.dirname(self.find_manifest()))

        if self.config.chroot:
            subprocess.check_call(shlex.split(command), cwd=self.config.dir)
        else:
            # Run this in the container so the host doesn't need to have click installed
            self.run_container_command(command)

        self.click_review()

        if self.config.click_output:
            click = '{}_{}_{}.click'.format(self.find_package_name(), self.find_version(), self.config.arch)
            click_path = os.path.join(self.config.dir, click)
            output_file = os.path.join(self.config.click_output, click)

            if not os.path.exists(self.config.click_output):
                os.makedirs(self.config.click_output)

            print_info('Click outputted to {}'.format(output_file))
            shutil.copyfile(click_path, output_file)

    def click_review(self):
        pass  # TODO implement this

    def install(self, click_path=None):
        if self.config.desktop:
            print_warning('Skipping install, running in desktop mode')
            return
        elif self.config.container_mode:
            print_warning('Skipping install, running in container mode')
            return

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
                self.check_multiple_devices()
                command = 'adb push {} /home/phablet/'.format(click_path)
            subprocess.check_call(command, cwd=cwd, shell=True)

        self.run_device_command('pkcon install-local --allow-untrusted {}'.format(click), cwd=cwd)

    def kill(self):
        if self.config.desktop:
            print_warning('Skipping kill, running in desktop mode')
            return
        elif self.config.container_mode:
            print_warning('Skipping kill, running in container mode')
            return

        if self.config.kill:
            try:
                self.run_device_command('pkill {}'.format(self.config.kill))
            except Exception:
                pass  # Nothing to do, the process probably wasn't running

    def desktop_launch(self):
        if self.config.lxd:
            raise Exception('Using lxd for desktop mode is not supported')

        desktop_path = None
        hooks = self.get_manifest().get('hooks', {})
        if self.config.app:
            if self.config.app in hooks and 'desktop' in hooks[self.config.app]:
                desktop_path = hooks[self.config.app]['desktop']
        else:
            for key, value in hooks.items():
                if 'desktop' in value:
                    desktop_path = value['desktop']
                    break

        if not desktop_path:
            raise Exception('Could not find desktop file for app "{}"'.format(self.config.app))

        desktop_path = os.path.join(self.temp, desktop_path)
        if not os.path.exists(desktop_path):
            raise Exception('Could not desktop file does not exist: "{}"'.format(desktop_path))

        execute = None
        with open(desktop_path, 'r') as desktop_file:
            lines = desktop_file.readlines()
            for line in lines:
                if line.startswith('Exec='):
                    execute = line.replace('Exec=', '')
                    break

        if not execute:
            raise Exception('No "Exec" line found in the desktop file')
        else:
            execute = execute.strip()

        # Inspired by https://stackoverflow.com/a/1160227
        xauth = '/tmp/.docker.xauth'
        with open(xauth, 'a'):
            os.utime(xauth, None)

        self.check_docker()

        share = '/tmp/clickable/share'
        if not os.path.isdir(share):
            os.makedirs(share)

        cache = '/tmp/clickable/cacge'
        if not os.path.isdir(cache):
            os.makedirs(cache)

        config = '/tmp/clickable/config'
        if not os.path.isdir(config):
            os.makedirs(config)

        volumes = '-v {}:{} -v /tmp/.X11-unix:/tmp/.X11-unix -v {}:{} -v {}:/tmp/.local/share -v {}:/tmp/.cache -v {}:/tmp/.config'.format(
            self.cwd,
            self.cwd,
            xauth,
            xauth,
            share,
            cache,
            config,
        )

        if self.config.use_nvidia:
            volumes += ' -v /dev/snd/pcmC2D0c:/dev/snd/pcmC2D0c -v /dev/snd/controlC2:/dev/snd/controlC2 --device /dev/snd'

        lib_path = os.path.join(self.temp, 'lib/x86_64-linux-gnu:/usr/local/nvidia/lib:/usr/local/nvidia/lib64')
        path = '/usr/local/nvidia/bin:/bin:/usr/bin:{}:{}:{}'.format(
            os.path.join(self.temp, 'bin'),
            os.path.join(self.temp, 'lib/x86_64-linux-gnu/bin'),
            self.temp,
        )
        environment = '-e XAUTHORITY=/tmp/.docker.xauth -e DISPLAY={} -e QML2_IMPORT_PATH={} -e LD_LIBRARY_PATH={} -e PATH={} -e HOME=/tmp -e OXIDE_NO_SANDBOX=1'.format(
            os.environ['DISPLAY'],
            lib_path,
            lib_path,
            path,
        )

        if execute.startswith('webapp-container'):
            # This is needed for the webapp-container, so only do it for this case
            volumes = '{} -v /etc/passwd:/etc/passwd'.format(volumes)
            environment = '{} -e APP_ID={}'.format(environment, self.find_package_name())

        go_config = ''
        if self.config.gopath:
            go_config = '-v {}:/gopath -e GOPATH=/gopath'.format(self.config.gopath)

        run_xhost = False
        try:
            self.check_command('xhost')
            run_xhost = True
        except Exception:  # TODO catch a specific Exception
            print_warning('xhost not installed, desktop mode may fail')
            run_xhost = False

        if run_xhost:
            subprocess.check_call(shlex.split('xhost +local:docker'))

        command = '{} run {} {} {} -w {} -u {} --rm -i {} bash -c "{}"'.format(
            'nvidia-docker' if self.config.use_nvidia else 'docker',
            volumes,
            go_config,
            environment,
            self.temp,
            os.getuid(),
            self.docker_image,
            execute,
        )

        subprocess.check_call(shlex.split(command), cwd=self.temp)

    def launch(self, app=None):
        cwd = '.'
        if not app:
            app = '{}_{}_{}'.format(self.find_package_name(), self.find_app_name(), self.find_version())
            cwd = self.config.dir

        launch = 'ubuntu-app-launch {}'.format(app)
        if self.config.launch:
            launch = self.config.launch

        if self.config.desktop:
            self.desktop_launch()
        else:
            self.run_device_command('sleep 1s && {}'.format(launch), cwd=cwd)

    def logs(self):
        if self.config.desktop:
            print_warning('Skipping logs, running in desktop mode')
            return
        elif self.config.container_mode:
            print_warning('Skipping logs, running in container mode')
            return

        log = '~/.cache/upstart/application-click-{}_{}_{}.log'.format(self.find_package_name(), self.find_app_name(), self.find_version())

        if self.config.log:
            log = self.config.log

        self.run_device_command('tail -f {}'.format(log))

    def clean(self):
        if os.path.exists(self.config.dir):
            try:
                shutil.rmtree(self.config.dir)
            except Exception:
                type, value, traceback = sys.exc_info()
                if type == OSError and 'No such file or directory' in value:  # TODO see if there is a proper way to do this
                    pass  # Nothing to do here, the directory didn't exist
                else:
                    print_warning('Failed to clean the build directory: {}: {}'.format(type, value))

        if os.path.exists(self.temp):
            try:
                shutil.rmtree(self.temp)
            except Exception:
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
        except Exception:
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

    def toggle_ssh(self, on=False):
        command = 'sudo -u phablet bash -c \'/usr/bin/gdbus call -y -d com.canonical.PropertyService -o /com/canonical/PropertyService -m com.canonical.PropertyService.SetProperty ssh {}\''.format(
            'true' if on else 'false'
        )

        adb_args = ''
        if self.device_serial_number:
            adb_args = '-s {}'.format(self.device_serial_number)

        run_subprocess_call(shlex.split('adb {} shell "{}"'.format(adb_args, command)), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def shell(self):
        '''
        Inspired by http://bazaar.launchpad.net/~phablet-team/phablet-tools/trunk/view/head:/phablet-shell
        '''

        if self.config.ssh:
            subprocess.check_call(shlex.split('ssh phablet@{}'.format(self.config.ssh)))
        else:

            adb_args = ''
            if self.device_serial_number:
                adb_args = '-s {}'.format(self.device_serial_number)
            else:
                self.check_multiple_devices()

            output = run_subprocess_check_output(shlex.split('adb {} shell pgrep sshd'.format(adb_args))).split()
            if not output:
                self.toggle_ssh(on=True)

            # Use the usb cable rather than worrying about going over wifi
            port = 0
            for p in range(2222, 2299):
                error_code = run_subprocess_call(shlex.split('adb {} forward tcp:{} tcp:22'.format(adb_args, p)), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if error_code == 0:
                    port = p
                    break

            if port == 0:
                raise Exception('Failed to open a port to the device')

            # Purge the device host key so that SSH doesn't print a scary warning about it
            # (it changes every time the device is reflashed and this is expected)
            known_hosts = os.path.expanduser('~/.ssh/known_hosts')
            subprocess.check_call(shlex.split('touch {}'.format(known_hosts)))
            subprocess.check_call(shlex.split('ssh-keygen -f {} -R [localhost]:{}'.format(known_hosts, port)))

            id_pub = os.path.expanduser('~/.ssh/id_rsa.pub')
            if not os.path.isfile(id_pub):
                raise Exception('Could not find a ssh public key at "{}", please generate one and try again'.format(id_pub))

            with open(id_pub, 'r') as f:
                public_key = f.read().strip()

            self.run_device_command('[ -d ~/.ssh ] || mkdir ~/.ssh', cwd=self.cwd)
            self.run_device_command('touch  ~/.ssh/authorized_keys', cwd=self.cwd)

            output = run_subprocess_check_output('adb {} shell "grep \\"{}\\" ~/.ssh/authorized_keys"'.format(adb_args, public_key), shell=True).strip()
            if not output or 'No such file or directory' in output:
                print_info('Inserting ssh public key on the connected device')
                self.run_device_command('echo \"{}\" >>~/.ssh/authorized_keys'.format(public_key), cwd=self.cwd)
                self.run_device_command('chmod 700 ~/.ssh', cwd=self.cwd)
                self.run_device_command('chmod 600 ~/.ssh/authorized_keys', cwd=self.cwd)

            subprocess.check_call(shlex.split('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -p {} phablet@localhost'.format(port)))
            self.toggle_ssh(on=False)

    def detect_devices(self):
        output = run_subprocess_check_output(shlex.split('adb devices -l')).strip()
        devices = []
        for line in output.split('\n'):
            if 'device' in line and 'devices' not in line:
                device = line.split(' ')[0]
                for part in line.split(' '):
                    if part.startswith('model:'):
                        device = '{} - {}'.format(device, part.replace('model:', '').replace('_', ' ').strip())

                devices.append(device)

        return devices

    def check_multiple_devices(self):
        devices = self.detect_devices()
        if len(devices) > 1 and not self.device_serial_number:
            raise Exception('Multiple devices attached')

    def devices(self):
        devices = self.detect_devices()

        if len(devices) == 0:
            print_warning('No attached devices')
        else:
            for device in devices:
                print_info(device)

    def init_app(self, name=None):
        if not cookiecutter_available:
            raise Exception('Cookiecutter is not available on your computer, more information can be found here: https://cookiecutter.readthedocs.io/en/latest/installation.html#install-cookiecutter')

        app_templates = [
            {
                'name': 'pure-qml-cmake',
                'display': 'Pure QML App (built using CMake)',
                'url': 'https://github.com/bhdouglass/ut-app-pure-qml-cmake-template',
            }, {
                'name': 'cmake',
                'display': 'C++/QML App (built using CMake)',
                'url': 'https://github.com/bhdouglass/ut-app-cmake-template',
            }, {
                'name': 'python-cmake',
                'display': 'Python/QML App (built using CMake)',
                'url': 'https://github.com/bhdouglass/ut-app-python-cmake-template',
            }, {
                'name': 'html',
                'display': 'HTML App',
                'url': 'https://github.com/bhdouglass/ut-app-html-template',
            }, {
                'name': 'webapp',
                'display': 'Simple Webapp',
                'url': 'https://github.com/bhdouglass/ut-app-webapp-template',
            }, {
                'name': 'go',
                'display': 'Go/QML App',
                'url': 'https://github.com/bhdouglass/ut-app-go-template',
            }
        ]

        app_template = None
        if name:
            for template in app_templates:
                if template['name'] == name:
                    app_template = template

        if not app_template:
            print_info('Available app templates:')
            for (index, template) in enumerate(app_templates):
                print('[{}] {} - {}'.format(index + 1, template['name'], template['display']))

            choice = input('Choose an app template [1]: ').strip()
            if not choice:
                choice = '1'

            try:
                choice = int(choice)
            except ValueError:
                raise Exception('Invalid choice')

            if choice > len(app_templates) or choice < 1:
                raise Exception('Invalid choice')

            app_template = app_templates[choice - 1]

        print_info('Generating new app from template: {}'.format(app_template['display']))
        cookiecutter(app_template['url'])

        print_info('Your new app has been generated, go to the app\'s directory and run clickable to get started')

    def run(self, command):
        self.setup_dependencies()
        self.run_container_command(command, use_dir=False)


class MakeClickable(Clickable):
    def pre_make(self):
        if self.config.premake:
            subprocess.check_call(self.config.premake, cwd=self.config.dir, shell=True)

    def post_make(self):
        if self.config.postmake:
            subprocess.check_call(self.config.postmake, cwd=self.config.dir, shell=True)

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
        except FileExistsError:
            print_warning('Failed to create temp dir, already exists')
        except Exception:
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
        command = None

        if self.build_arch == 'armhf':
            command = 'qt5-qmake-arm-linux-gnueabihf'
        elif self.build_arch == 'amd64':
            command = 'qmake'
        else:
            raise Exception('{} is not supported by the qmake build yet'.format(self.build_arch))

        self.run_container_command('{} {}'.format(command, self.cwd))

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
            # TODO ignore version control directories by default
            if (
                cpath == os.path.abspath(self.temp) or
                cpath == os.path.abspath(self.config.dir) or
                content in self.config.ignore or
                content == 'clickable.json'
            ):
                ignored.append(content)

        return ignored

    def _build(self):
        shutil.copytree(self.cwd, self.temp, ignore=self._ignore)
        print_info('Copied files to temp directory for click building')


class PythonClickable(PureClickable):
    # The only difference between this and the Pure template is that this doesn't force the "all" arch
    pass


class GoClickable(Clickable):
    def _ignore(self, path, contents):
        ignored = []
        for content in contents:
            cpath = os.path.abspath(os.path.join(path, content))
            if (
                cpath == os.path.abspath(self.temp) or
                cpath == os.path.abspath(self.config.dir) or
                content in self.config.ignore or
                content == 'clickable.json' or

                # Don't copy the go files, they will be compiled from the source directory
                os.path.splitext(content)[1] == '.go'
            ):
                ignored.append(content)

        return ignored

    def _build(self):
        shutil.copytree(self.cwd, self.temp, ignore=self._ignore)

        gocommand = '/usr/local/go/bin/go build -pkgdir {}/.clickable/go -i -o {}/{} ..'.format(
            self.cwd,
            self.temp,
            self.find_app_name(),
        )
        self.run_container_command(gocommand)


class CordovaClickable(CMakeClickable):
    # Lots of this code was based off of this:
    # https://github.com/apache/cordova-ubuntu/blob/28cd3c1b53c1558baed4c66cb2deba597f05b3c6/bin/templates/project/cordova/lib/build.js#L59-L131
    def __init__(self, *args, **kwargs):
        super(CMakeClickable, self).__init__(*args, **kwargs)

        self.platform_dir = os.path.join(self.cwd, 'platforms/ubuntu/')

        self._dirs = {
            'build': '{}/{}/{}/build/' .format(self.platform_dir, self.config.sdk, self.build_arch),
            'prefix': '{}/{}/{}/prefix/'.format(self.platform_dir, self.config.sdk, self.build_arch),
            'make': '{}/build'.format(self.platform_dir)
        }

        self.temp = self._dirs['build']

        if not os.path.isdir(self.platform_dir):
            # fail when not using docker, need it anyways
            if self.config.container_mode or self.config.lxd or self.config.chroot:
                print_error('Docker is required to intialize cordova directories. Enable docker or run "cordova platform add ubuntu" manually to remove this message')
                sys.exit(1)

            cordova_docker_image = "beevelop/cordova:v7.0.0"
            command = "cordova platform add ubuntu"

            # Can't use self.run_container_command because need to set -e HOME=/tmp
            wrapped_command = 'docker run -v {cwd}:{cwd} -w {cwd} -u {uid}:{uid} -e HOME=/tmp --rm -i {img} {cmd}'.format(
                cwd=self.cwd,
                uid=os.getuid(),
                img=cordova_docker_image,
                cmd=command
            )

            subprocess.check_call(shlex.split(wrapped_command))

        self.config.dir = self._dirs['prefix']

    def _build(self):

        # Clear out prefix directory
        # IK this is against DRY, but I copied this code from MakeClickable.make_install
        if os.path.exists(self.config.dir) and os.path.isdir(self.temp):
            shutil.rmtree(self.config.dir)

        try:
            os.makedirs(self.config.dir)
        except FileExistsError:
            print_warning('Failed to create temp dir, already exists')
        except Exception:
            print_warning('Failed to create temp dir ({}): {}'.format(self.temp, str(sys.exc_info()[0])))

        self.run_container_command('cmake {} -DCMAKE_INSTALL_PREFIX={}'.format(self._dirs['make'], self._dirs['build']))

        super(CMakeClickable, self)._build()

    def post_make(self):
        super(CordovaClickable, self).post_make()

        www_dir = os.path.join(self.platform_dir, "www")
        shutil.rmtree(www_dir)
        shutil.copytree(os.path.join(self.cwd, "www"), www_dir)
        shutil.copyfile(os.path.join(self.cwd, "config.xml"), os.path.join(www_dir, 'config.xml'))

        copies = {
                "www": None,
                "platform_www": "www",
                "config.xml": None,
                "cordova.desktop": None,
                "manifest.json": None,
                "apparmor.json": None,
                }

        # If value is none, set to key
        copies = {key: key if value is None else value
                  for key, value in copies.items()}

        # Is this overengineerd?
        for file_to_copy_source, file_to_copy_dest in copies.items():
            full_source_path = os.path.join(self.platform_dir,
                                            file_to_copy_source)
            full_dest_path = os.path.join(self._dirs['build'],
                                          file_to_copy_dest)
            if os.path.isdir(full_source_path):
                # https://stackoverflow.com/a/31039095/6381767
                copy_tree(full_source_path, full_dest_path)
            else:
                shutil.copy(full_source_path, full_dest_path)

        # Modify default files with updated settings
        # taken straing from cordova build.js
        with open(self.find_manifest(), 'r') as manifest_reader:
            manifest = json.load(manifest_reader)
            manifest['architecture'] = self.build_arch
            manifest['framework'] = self.config.sdk
            with open(self.find_manifest(), 'w') as manifest_writer:
                json.dump(manifest, manifest_writer, indent=4)

        apparmor_file = os.path.join(self._dirs['build'], 'apparmor.json')
        with open(apparmor_file, 'r') as apparmor_reader:
            apparmor = json.load(apparmor_reader)
            apparmor["policy_version"] = 1.3

            if 'webview' not in apparmor["policy_groups"]:
                apparmor["policy_groups"].append("webview")

            with open(apparmor_file, 'w') as apparmor_writer:
                json.dump(apparmor, apparmor_writer, indent=4)

    def make_install(self):
        # This is beause I don't want a DESTDIR
        self.run_container_command('make install')

    def find_manifest(self):
        return find_manifest(self._dirs['build'])

    def get_manifest(self):
        return get_manifest(self._dirs['build'])

    def find_package_name(self):
        tree = ElementTree.parse('config.xml')
        root = tree.getroot()
        return root.attrib['id'] if 'id' in root.attrib else '1.0.0'

    def find_version(self):
        tree = ElementTree.parse('config.xml')
        root = tree.getroot()
        return root.attrib['version'] if 'version' in root.attrib else '1.0.0'


def main():
    config = None
    COMMAND_ALIASES = {
        'click_build': 'click_build',
        'build_click': 'click_build',
        'build-click': 'click_build',
    }

    COMMAND_HANDLERS = {
        'kill': 'kill',
        'clean': 'clean',
        'build': 'build',
        'click-build': 'click_build',
        'install': 'install',
        'launch': 'launch',
        'logs': 'logs',
        'setup-lxd': 'setup_lxd',
        'display-on': 'display_on',
        'no-lock': 'no_lock',
        'setup-docker': 'setup_docker',
        'shell': 'shell',
        'devices': 'devices',
        'init': 'init_app',
        'run': 'run',
    }

    def show_valid_commands():
        n = [
            'Valid commands:',
            ', '.join(sorted(COMMAND_HANDLERS.keys()))
        ]
        if config and hasattr(config, 'scripts') and config.scripts:
            n += [
                'Project-specific custom commands:',
                ', '.join(sorted(config.scripts.keys()))
            ]
        return '\n'.join(n)

    def print_valid_commands():
        print(show_valid_commands())

    parser = argparse.ArgumentParser(description='clickable')
    parser.add_argument('--version', '-v', action='version',
                        version='%(prog)s ' + __version__)
    parser.add_argument('commands', nargs='*', help=show_valid_commands())
    parser.add_argument(
        '--device',
        '-d',
        action='store_true',
        help='Whether or not to run the custom command on the device',
        default=False,
    )
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

    # TODO depricate
    parser.add_argument(
        '--click',
        '-c',
        help='Installs the specified click (use with the "install" command)'
    )

    # TODO depricate
    parser.add_argument(
        '--app',
        '-p',
        help='Launches the specified app (use with the "launch" command)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Runs in debug mode',
        default=False,
    )
    parser.add_argument(
        '--lxd',
        action='store_true',
        help='Run build commands in a lxd container',
        default=False,
    )
    parser.add_argument(
        '--output',
        help='Where to output the compiled click package',
    )
    parser.add_argument(
        '--container-mode',
        action='store_true',
        help='Run all build commands on the current machine and not a container',
        default=False,
    )
    parser.add_argument(
        '--name',
        '-n',
        help='Specify an app template name to use when running "clickable init"'
    )
    parser.add_argument(
        '--desktop',
        '-e',
        action='store_true',
        help='Run the app on the current machine for testing',
        default=False,
    )
    parser.add_argument(
        '--sdk',
        '-k',
        help='Use a specific version of the ubuntu sdk to compile against',
    )
    parser.add_argument(
        '--nvidia',
        action='store_true',
        help='Use nvidia-docker rather than docker',
        default=False,
    )

    args = parser.parse_args()

    skip_detection = False
    if args.click:
        skip_detection = True

    if len(args.commands) == 1:
        skip_commands = [
            'setup-lxd',
            'setup-docker',
            'shell',
            'no-lock',
            'display-on',
            'devices',
            'init',
        ]

        if args.commands[0] in skip_commands:
            skip_detection = True

    try:
        # TODO clean this up
        config = Config(
            ip=args.ip,
            arch=args.arch,
            template=args.template,
            skip_detection=skip_detection,
            lxd=args.lxd,
            click_output=args.output,
            container_mode=args.container_mode,
            desktop=args.desktop,
            sdk=args.sdk,
            use_nvidia=args.nvidia,
        )

        VALID_COMMANDS = list(COMMAND_HANDLERS.keys()) + list(config.scripts.keys())

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
        elif config.template == config.GO:
            clickable = GoClickable(config, args.device_serial_number)

        commands = args.commands
        if len(args.commands) == 0:
            commands = config.default.split(' ')

        '''
        Detect senarios when an argument is passed to a command. For example:
        `clickable install /path/to/click`. Since clickable allows commands
        to be strung together it makes detecting this harder. This check has
        been limited to just the case when we have 2 values in args.commands as
        stringing together multiple commands and a command with an argument is
        unlikely to occur.
        TODO determine if there is a better way to do this.
        '''
        command_arg = ''
        if len(commands) == 2 and commands[1] not in VALID_COMMANDS:
            command_arg = commands[1]
            commands = commands[:1]

        # TODO consider removing the ability to string together multiple commands
        # This should help clean up the arguments & new command_arg
        for command in commands:
            if command in config.scripts:
                clickable.script(command, args.device)
            elif command == 'install':
                clickable.install(args.click if args.click else command_arg)
            elif command == 'launch':
                clickable.launch(args.app if args.app else command_arg)
            elif command == 'init':
                clickable.init_app(args.name)
            elif command == 'run':
                if not command_arg:
                    raise ValueError('No command supplied for `clickable run`')

                clickable.run(command_arg)
            elif command in COMMAND_HANDLERS:
                getattr(clickable, COMMAND_HANDLERS[command])()
            elif command in COMMAND_ALIASES:
                getattr(clickable, COMMAND_ALIASES[command])()
            elif command == 'help':
                parser.print_help()
            else:
                print_error('There is no builtin or custom command named "{}"'.format(command))
                print_valid_commands()
    except Exception:
        if args.debug:
            raise
        else:
            print_error(str(sys.exc_info()[1]))
            sys.exit(1)


if __name__ == '__main__':
    main()
