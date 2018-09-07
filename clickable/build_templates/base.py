import subprocess
import shlex
import json
import shutil
import time
import uuid
import sys
import os
import getpass
import requests

from clickable.utils import (
    run_subprocess_call,
    run_subprocess_check_output,
    print_info,
    print_success,
    print_warning,
    print_error,
    find_manifest,
    get_manifest,
)

cookiecutter_available = True
try:
    from cookiecutter.main import cookiecutter
except ImportError:
    cookiecutter_available = False


# TODO break this up into different files per command

OPENSTORE_API = 'https://open-store.io'
OPENSTORE_API_PATH = '/api/v3/manage/{}/revision'


class Clickable(object):
    cwd = None
    first_docker_info = True

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
            if self.config.lxd:
                print_warning('Use of lxd is deprecated and will be removed in a future version')
                self.check_command('usdk-target')
            else:
                self.check_command('docker')

                if self.config.docker_image:
                    self.docker_image = self.config.docker_image
                    self.base_docker_image = self.docker_image
                else:
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
            self.check_any_devices()

            if self.device_serial_number:
                wrapped_command = 'adb -s {} shell "{}"'.format(self.device_serial_number, command)
            else:
                self.check_multiple_devices()
                wrapped_command = 'adb shell "{}"'.format(command)

        subprocess.check_call(wrapped_command, cwd=cwd, shell=True)

    def run_container_command(self, command, force_lxd=False, sudo=False, get_output=False, use_dir=True, cwd=None):
        wrapped_command = command
        cwd = cwd if cwd else self.cwd

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
        else:  # Docker
            self.check_docker()

            if ' ' in cwd or ' ' in self.config.dir:
                raise Exception('There are spaces in the current path, this will cause errors in the build process')

            if self.first_docker_info:
                print_info('Using docker container "{}"'.format(self.base_docker_image))
                self.first_docker_info = False

            go_config = ''
            if self.config.gopath:
                go_config = '-v {}:/gopath -e GOPATH=/gopath'.format(self.config.gopath)

            wrapped_command = 'docker run -v {}:{} {} -w {} -u {} -e HOME=/tmp --rm -i {} bash -c "{}"'.format(
                cwd,
                cwd,
                go_config,
                self.config.dir if use_dir else cwd,
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

            if self.config.lxd or self.config.container_mode:
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

                if self.config.docker_image:
                    print_info('Skipping dependency check, using a custom docker image')
                else:
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
                        try:
                            subprocess.check_call(shlex.split('docker build -t {} .'.format(self.docker_image)), cwd='.clickable')
                        except subprocess.CalledProcessError:
                            self.clean_clickable()
                            raise
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

    def update_docker(self):
        self.check_docker()

        subprocess.check_call(shlex.split('docker pull {}'.format(self.base_docker_image)))

    def display_on(self):
        command = 'powerd-cli display on'
        self.run_device_command(command, cwd=self.cwd)

    def no_lock(self):
        print_info('Turning off device activity timeout')
        command = 'gsettings set com.ubuntu.touch.system activity-timeout 0'
        self.run_device_command(command, cwd=self.cwd)

    def click_build(self):
        command = 'click build {} --no-validate'.format(os.path.dirname(self.find_manifest()))

        self.run_container_command(command)

        if self.config.click_output:
            click = '{}_{}_{}.click'.format(self.find_package_name(), self.find_version(), self.config.arch)
            click_path = os.path.join(self.config.dir, click)
            output_file = os.path.join(self.config.click_output, click)

            if not os.path.exists(self.config.click_output):
                os.makedirs(self.config.click_output)

            print_info('Click outputted to {}'.format(output_file))
            shutil.copyfile(click_path, output_file)

    def click_review(self, click_path=None):
        if click_path:
            click = os.path.basename(click_path)
        else:
            click = '{}_{}_{}.click'.format(self.find_package_name(), self.find_version(), self.config.arch)
            click_path = os.path.join(self.config.dir, click)

        cwd = os.path.dirname(os.path.realpath(click_path))
        self.run_container_command('click-review {}'.format(click_path), use_dir=False, cwd=cwd)

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
            self.check_any_devices()

            if self.device_serial_number:
                command = 'adb -s {} push {} /home/phablet/'.format(self.device_serial_number, click_path)
            else:
                self.check_multiple_devices()
                command = 'adb push {} /home/phablet/'.format(click_path)
            subprocess.check_call(command, cwd=cwd, shell=True)

        self.run_device_command('pkcon install-local --allow-untrusted /home/phablet/{}'.format(click), cwd=cwd)

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

        lib_path = ':'.join([
            os.path.join(self.temp, 'lib/x86_64-linux-gnu'),
            os.path.join(self.temp, 'lib'),
            '/usr/local/nvidia/lib',
            '/usr/local/nvidia/lib64',
        ])

        path = ':'.join([
            '/usr/local/nvidia/bin',
            '/bin',
            '/usr/bin',
            os.path.join(self.temp, 'bin'),
            os.path.join(self.temp, 'lib/x86_64-linux-gnu/bin'),
            self.temp,
        ])
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

    def clean_clickable(self):
        path = os.path.join(self.cwd, '.clickable')
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
            except Exception:
                type, value, traceback = sys.exc_info()
                if type == OSError and 'No such file or directory' in value:  # TODO see if there is a proper way to do this
                    pass  # Nothing to do here, the directory didn't exist
                else:
                    raise

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
            self.check_any_devices()

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

    def check_any_devices(self):
        devices = self.detect_devices()
        if len(devices) == 0:
            raise Exception('No devices available via adb')

    def check_multiple_devices(self):
        devices = self.detect_devices()
        if len(devices) > 1 and not self.device_serial_number:
            raise Exception('Multiple devices detected via adb')

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

    def writable_image(self):
        command = 'dbus-send --system --print-reply --dest=com.canonical.PropertyService /com/canonical/PropertyService com.canonical.PropertyService.SetProperty string:writable boolean:true'
        self.run_device_command(command, cwd=self.cwd)
        print_info('Rebooting for writable image')

    def publish(self):
        # TODO allow publishing app for the first time

        if not self.config.apikey:
            print_error('No api key specified, use OPENSTORE_API_KEY or --apikey')
            return

        click = '{}_{}_{}.click'.format(self.find_package_name(), self.find_version(), self.config.arch)
        click_path = os.path.join(self.config.dir, click)

        url = OPENSTORE_API
        if 'OPENSTORE_API' in os.environ and os.environ['OPENSTORE_API']:
            url = os.environ['OPENSTORE_API']

        url = url + OPENSTORE_API_PATH.format(self.find_package_name())
        channel = 'xenial' if self.config.is_xenial else 'vivid'
        files = {'file': open(click_path, 'rb')}
        data = {'channel': channel}
        params = {'apikey': self.config.apikey}

        print_info('Uploading version {} of {} for {} to the OpenStore'.format(self.find_version(), self.find_package_name(), channel))
        response = requests.post(url, files=files, data=data, params=params)
        if response.status_code == requests.codes.ok:
            print_success('Upload successful')
        else:
            if response.text == 'Unauthorized':
                print_error('Failed to upload click: Unauthorized')
            else:
                print_error('Failed to upload click: {}'.format(response.json()['message']))
