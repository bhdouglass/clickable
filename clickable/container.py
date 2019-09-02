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
    check_command,
    image_exists,
)
from clickable.config import Config


class Container(object):
    def __init__(self, config, name=None):
        self.config = config
        self.clickable_dir = '.clickable/{}'.format(self.config.build_arch)
        if name:
            self.clickable_dir = '{}/{}'.format(self.clickable_dir, name)
        self.docker_name_file = '{}/name.txt'.format(self.clickable_dir)
        self.docker_file = '{}/Dockerfile'.format(self.clickable_dir)

        if not self.config.container_mode:
            check_command('docker')

            self.docker_image = self.config.docker_image
            self.base_docker_image = self.docker_image

            if self.docker_image in self.config.container_list:
                self.base_docker_image = self.docker_image

                if os.path.exists(self.docker_name_file):
                    self.restore_cached_container()

    def restore_cached_container(self):
        with open(self.docker_name_file, 'r') as f:
            cached_container = f.read().strip()

            if not image_exists(cached_container):
                print_info("Cached container does not exist anymore")
                return

            command_base = 'docker images -q {}'.format(self.base_docker_image)
            command_cached = 'docker history -q {}'.format(cached_container)

            hash_base = run_subprocess_check_output(command_base).strip()
            history_cached = run_subprocess_check_output(command_cached).strip()

            if hash_base in history_cached:
                print_info("Found cached container")
                self.docker_image = cached_container
            else:
                print_info("Found outdated container")

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

    def run_command(self, command, sudo=False, get_output=False, use_dir=True, cwd=None):
        wrapped_command = command
        cwd = cwd if cwd else os.path.abspath(self.config.root_dir)

        if self.config.container_mode:
            wrapped_command = 'bash -c "{}"'.format(command)
        else:  # Docker
            self.check_docker()

            if ' ' in cwd or ' ' in self.config.build_dir:
                raise Exception('There are spaces in the current path, this will cause errors in the build process')

            if self.config.first_docker_info:
                print_info('Using docker container "{}"'.format(self.docker_image))
                self.config.first_docker_info = False

            go_config = ''
            if self.config.gopath:
                gopaths = self.config.gopath.split(':')

                docker_gopaths = []
                go_configs = []
                for (index, path) in enumerate(gopaths):
                    go_configs.append('-v {}:/gopath/path{}:Z'.format(path, index))
                    docker_gopaths.append('/gopath/path{}'.format(index))

                go_config = '{} -e GOPATH={}'.format(
                    ' '.join(go_configs),
                    ':'.join(docker_gopaths),
                )

            rust_config = ''

            if self.config.config['template'] == Config.RUST and self.config.cargo_home:
                cargo_registry = os.path.join(self.config.cargo_home, 'registry')
                cargo_git = os.path.join(self.config.cargo_home, 'git')
                cargo_package_cache_lock = os.path.join(self.config.cargo_home, '.package-cache')

                os.makedirs(cargo_registry, exist_ok=True)
                os.makedirs(cargo_git, exist_ok=True)

                # create .package-cache if it doesn't exist
                with open(cargo_package_cache_lock, "a"):
                    pass

                rust_config = '-v {}:/opt/rust/cargo/registry:Z -v {}:/opt/rust/cargo/git:Z -v {}:/opt/rust/cargo/.package-cache'.format(
                    cargo_registry,
                    cargo_git,
                    cargo_package_cache_lock,
                )

            wrapped_command = 'docker run -v {}:{}:Z {} {} -w {} -u {} -e HOME=/tmp --rm -i {} bash -c "{}"'.format(
                cwd,
                cwd,
                go_config,
                rust_config,
                self.config.build_dir if use_dir else cwd,
                os.getuid(),
                self.docker_image,
                command,
            )

        kwargs = {}
        if use_dir:
            kwargs['cwd'] = self.config.build_dir

        if get_output:
            return run_subprocess_check_output(shlex.split(wrapped_command), **kwargs)
        else:
            subprocess.check_call(shlex.split(wrapped_command), **kwargs)

    def setup_dependencies(self, force_build=False):
        if self.config.dependencies_build or self.config.dependencies_target:
            print_info('Checking dependencies')

            dependencies = self.config.dependencies_build
            for dep in self.config.dependencies_target:
                if ':' in dep:
                    dependencies.append(dep)
                else:
                    dependencies.append('{}:{}'.format(dep, self.config.arch))

            self.check_docker()

            if self.config.custom_docker_image:
                print_info('Skipping dependency check, using a custom docker image')
            else:
                command_ppa = ''
                if self.config.dependencies_ppa:
                    command_ppa = 'RUN add-apt-repository {}'.format(' '.join(self.config.dependencies_ppa))
                dockerfile = '''
FROM {}
RUN echo set debconf/frontend Noninteractive | debconf-communicate && echo set debconf/priority critical | debconf-communicate
{}
RUN apt-get update && apt-get install -y --force-yes --no-install-recommends {} && apt-get clean
                '''.format(
                    self.base_docker_image,
                    command_ppa,
                    ' '.join(dependencies)
                ).strip()

                build = force_build

                if not os.path.exists(self.clickable_dir):
                    os.makedirs(self.clickable_dir)

                if self.docker_image != self.base_docker_image and os.path.exists(self.docker_file):
                    with open(self.docker_file, 'r') as f:
                        if dockerfile.strip() != f.read().strip():
                            build = True
                else:
                    build = True

                if not build:
                    command = 'docker images -q {}'.format(self.docker_image)
                    image_exists = run_subprocess_check_output(command).strip()
                    build = not image_exists

                if build:
                    with open(self.docker_file, 'w') as f:
                        f.write(dockerfile)

                    self.docker_image = '{}-{}'.format(self.base_docker_image, uuid.uuid4())
                    with open(self.docker_name_file, 'w') as f:
                        f.write(self.docker_image)

                    print_info('Generating new docker image')
                    try:
                        subprocess.check_call(shlex.split('docker build -t {} .'.format(self.docker_image)), cwd=self.clickable_dir)
                    except subprocess.CalledProcessError:
                        self.clean_clickable()
                        raise
                else:
                    print_info('Dependencies already setup')

    def clean_clickable(self):
        path = os.path.join(self.config.cwd, self.clickable_dir)
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
            except Exception:
                type, value, traceback = sys.exc_info()
                if type == OSError and 'No such file or directory' in value:  # TODO see if there is a proper way to do this
                    pass  # Nothing to do here, the directory didn't exist
                else:
                    raise
