import subprocess
import time
import shlex
import json
import os
import shutil
import getpass
import uuid

from clickable.utils import (
    run_subprocess_call,
    run_subprocess_check_output,
    print_info,
    print_warning,
    check_command
)
from clickable.config import Config


class Container(object):
    def __init__(self, config):
        self.config = config
        self.clickableDir = '.clickable/{}'.format(self.config.build_arch)
        self.dockerNameFile = '{}/name.txt'.format(self.clickableDir)
        self.dockerFile = '{}/Dockerfile'.format(self.clickableDir)

        if not self.config.container_mode:
            if self.config.lxd:
                print_warning('Use of lxd is deprecated and will be removed in a future version')
                check_command('usdk-target')
            else:
                check_command('docker')

                self.docker_image = self.config.docker_image
                self.base_docker_image = self.docker_image

                if 'clickable/ubuntu-sdk' in self.docker_image:
                    if self.config.use_nvidia:
                        self.docker_image += '-nvidia'
                        check_command('nvidia-docker')

                    self.base_docker_image = self.docker_image

                    if os.path.exists(self.dockerNameFile):
                        with open(self.dockerNameFile, 'r') as f:
                            self.docker_image = f.read().strip()

    def start_docker(self):
        started = False
        error_code = run_subprocess_call(shlex.split('which systemctl'), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if error_code == 0:
            print_info('Asking for root to start docker')
            error_code = run_subprocess_call(shlex.split('sudo systemctl start docker'))

            started = (error_code == 0)

        return started

    def check_docker(self, retries=3):
        if self.needs_setup():
            self.setup_docker()

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
        name = 'clickable-{}'.format(self.config.build_arch)

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
        name = 'clickable-{}'.format(self.config.build_arch)

        # Check for existing container
        existing = run_subprocess_check_output(shlex.split('{} list'.format(self.usdk_target)))
        existing = json.loads(existing)

        found = False
        for container in existing:
            if container['name'] == name:
                found = True

        return found

    def docker_group_exists(self):
        group_exists = False
        with open('/etc/group', 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith('docker:'):
                    group_exists = True

        return group_exists

    def user_part_of_docker_group(self):
        output = run_subprocess_check_output(shlex.split('groups {}'.format(getpass.getuser()))).strip()

        # Test for exactly docker in the group list
        return (' docker ' in output or output.endswith(' docker') or output.startswith('docker ') or output == 'docker')

    def needs_setup(self):
        return (not self.docker_group_exists() or not self.user_part_of_docker_group())

    def setup_docker(self):
        print_info('Setting up docker')

        check_command('docker')
        self.start_docker()

        if not self.docker_group_exists():
            print_info('Asking for root to create docker group')
            subprocess.check_call(shlex.split('sudo groupadd docker'))

        if self.user_part_of_docker_group():
            print_info('Setup has already been completed')
        else:
            print_info('Asking for root to add the current user to the docker group')
            subprocess.check_call(shlex.split('sudo usermod -aG docker {}'.format(getpass.getuser())))

            raise Exception('Log out or restart to apply changes')

    def update_docker(self):
        self.check_docker()

        subprocess.check_call(shlex.split('docker pull {}'.format(self.base_docker_image)))

    def run_command(self, command, force_lxd=False, sudo=False, get_output=False, use_dir=True, cwd=None):
        wrapped_command = command
        cwd = cwd if cwd else self.config.cwd

        if self.config.container_mode:
            wrapped_command = 'bash -c "{}"'.format(command)
        elif force_lxd or self.config.lxd:
            self.check_lxd()

            target_command = 'exec'
            if sudo:
                target_command = 'maint'

            if use_dir:
                command = 'cd {}; {}'.format(self.config.dir, command)

            wrapped_command = 'usdk-target {} clickable-{} -- bash -c "{}"'.format(target_command, self.config.build_arch, command)
        else:  # Docker
            self.check_docker()

            if ' ' in cwd or ' ' in self.config.dir:
                raise Exception('There are spaces in the current path, this will cause errors in the build process')

            if self.config.first_docker_info:
                print_info('Using docker container "{}"'.format(self.docker_image))
                self.config.first_docker_info = False

            go_config = ''
            if self.config.gopath:
                go_config = '-v {}:/gopath -e GOPATH=/gopath'.format(self.config.gopath)

            rust_config = ''

            if self.config.config['template'] == Config.RUST and self.config.cargo_home:
                cargo_registry = os.path.join(self.config.cargo_home, 'registry')
                cargo_git = os.path.join(self.config.cargo_home, 'git')

                os.makedirs(cargo_registry, exist_ok=True)
                os.makedirs(cargo_git, exist_ok=True)

                rust_config = '-v {}:/opt/rust/cargo/registry -v {}:/opt/rust/cargo/git'.format(
                    cargo_registry,
                    cargo_git,
                )

            wrapped_command = 'docker run -v {}:{} {} {} -w {} -u {} -e HOME=/tmp --rm -i {} bash -c "{}"'.format(
                cwd,
                cwd,
                go_config,
                rust_config,
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
                self.run_command('apt-get update', sudo=True, use_dir=False)

                command = 'apt-get install -y --force-yes'
                run = False
                for dep in self.config.dependencies:
                    if self.config.arch == 'armhf' and 'armhf' not in dep and not self.config.specificDependencies:
                        dep = '{}:{}'.format(dep, self.config.arch)

                    exists = ''
                    try:
                        exists = self.run_command('dpkg -s {} | grep Status'.format(dep), get_output=True, use_dir=False)
                    except subprocess.CalledProcessError:
                        exists = ''

                    if exists.strip() != 'Status: install ok installed':
                        run = True
                        command = '{} {}'.format(command, dep)

                if run:
                    self.run_command(command, sudo=True, use_dir=False)
                else:
                    print_info('Dependencies already installed')
            else:  # Docker
                self.check_docker()

                if self.config.custom_docker_image:
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

                    if not os.path.exists(self.clickableDir):
                        os.makedirs(self.clickableDir)

                    if os.path.exists(self.dockerFile):
                        with open(self.dockerFile, 'r') as f:
                            if dockerfile.strip() != f.read().strip():
                                build = True
                    else:
                        build = True

                    if not build:
                        command = 'docker images -q {}'.format(self.docker_image)
                        image_exists = run_subprocess_check_output(command).strip()
                        build = not image_exists

                    if build:
                        with open(self.dockerFile, 'w') as f:
                            f.write(dockerfile)

                        self.docker_image = '{}-{}'.format(self.base_docker_image, uuid.uuid4())
                        with open(self.dockerNameFile, 'w') as f:
                            f.write(self.docker_image)

                        print_info('Generating new docker image')
                        try:
                            subprocess.check_call(shlex.split('docker build -t {} .'.format(self.docker_image)), cwd=self.clickableDir)
                        except subprocess.CalledProcessError:
                            self.clean_clickable()
                            raise
                    else:
                        print_info('Dependencies already setup')

    def clean_clickable(self):
        path = os.path.join(self.config.cwd, self.clickableDir)
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
            except Exception:
                type, value, traceback = sys.exc_info()
                if type == OSError and 'No such file or directory' in value:  # TODO see if there is a proper way to do this
                    pass  # Nothing to do here, the directory didn't exist
                else:
                    raise
