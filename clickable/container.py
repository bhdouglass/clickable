import subprocess
import time
import shlex
import os
import shutil
import getpass
import uuid
import sys

from clickable.utils import (
    run_subprocess_call,
    run_subprocess_check_call,
    run_subprocess_check_output,
    check_command,
    image_exists,
)
from clickable.logger import logger
from clickable.config.project import ProjectConfig
from clickable.config.constants import Constants
from clickable.exceptions import ClickableException


class Container(object):
    def __init__(self, config, name=None, minimum_version=None):
        self.config = config
        self.docker_mode = self.config.needs_docker()
        self.minimum_version = minimum_version
        self.docker_image = self.config.docker_image
        self.base_docker_image = self.docker_image

        if self.config.needs_clickable_image():
            self.clickable_dir = '.clickable/{}'.format(self.config.build_arch)
            if name:
                self.clickable_dir = '{}/{}'.format(self.clickable_dir, name)

            self.docker_name_file = '{}/name.txt'.format(self.clickable_dir)
            self.docker_file = '{}/Dockerfile'.format(self.clickable_dir)

            if self.needs_customized_container():
                self.restore_cached_container()

    def restore_cached_container(self):
        if not os.path.exists(self.docker_name_file):
            return

        with open(self.docker_name_file, 'r') as f:
            cached_container = f.read().strip()

            if not image_exists(cached_container):
                logger.warning("Cached container does not exist anymore")
                return

            self.check_docker()

            command_base = 'docker images -q {}'.format(self.base_docker_image)
            command_cached = 'docker history -q {}'.format(cached_container)

            hash_base = run_subprocess_check_output(command_base).strip()
            history_cached = run_subprocess_check_output(command_cached).strip()

            if hash_base in history_cached:
                logger.debug("Found cached container")
                self.docker_image = cached_container
            else:
                logger.warning("Cached container is outdated")

    def start_docker(self):
        started = False
        error_code = run_subprocess_call(shlex.split('which systemctl'), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if error_code == 0:
            logger.info('Asking for root to start docker')
            error_code = run_subprocess_call(shlex.split('sudo systemctl start docker'))

            started = (error_code == 0)

        return started

    def check_docker(self, retries=3):
        if not self.docker_mode:
            raise ClickableException("Container was not initialized with Container Mode. This seems to be a bug in Clickable.")

        if self.needs_docker_setup():
            self.setup_docker()

        try:
            run_subprocess_check_output(shlex.split('docker ps'), stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            retries -= 1
            if retries <= 0:
                raise ClickableException("Couldn't check docker. If you just installed Clickable you may need to reboot once.")

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

    def needs_docker_setup(self):
        return (
            sys.platform != 'darwin' and
            (not self.docker_group_exists() or not self.user_part_of_docker_group())
        )

    def setup_docker(self):
        logger.info('Setting up docker')

        self.start_docker()

        if not self.docker_group_exists():
            logger.info('Asking for root to create docker group')
            subprocess.check_call(shlex.split('sudo groupadd docker'))

        if self.user_part_of_docker_group():
            logger.info('Setup has already been completed')
        else:
            logger.info('Asking for root to add the current user to the docker group')
            subprocess.check_call(shlex.split('sudo usermod -aG docker {}'.format(getpass.getuser())))

            raise ClickableException('Log out or restart to apply changes')

    def pull_files(self, files, dst_parent):
        os.makedirs(dst_parent, exist_ok=True)

        if self.config.container_mode:
            for f in files:
                dst_path = os.path.join(dst_parent, os.path.basename(f))
                if os.path.isdir(f):
                    if os.path.exists(dst_path):
                        shutil.rmtree(dst_path)
                    shutil.copytree(f, dst_path)
                else:
                    if os.path.exists(dst_path):
                        os.remove(dst_path)
                    shutil.copy(f, dst_parent, follow_symlinks=False)
        else:  # Docker
            command_create = 'docker create -v {}:{}:Z {}'.format(
                    self.config.root_dir,
                    self.config.root_dir,
                    self.docker_image
            )
            container = run_subprocess_check_output(command_create).strip()

            for f in files:
                command_copy = 'docker cp {}:{} {}'.format(
                    container,
                    f,
                    dst_parent
                )
                run_subprocess_check_call(command_copy)

            command_remove = 'docker rm {}'.format(container)
            run_subprocess_check_call(command_remove, stdout=subprocess.DEVNULL)

    def run_command(self, command, root_user=False, get_output=False,
            use_build_dir=True, cwd=None, tty=False, localhost=False):
        wrapped_command = command
        cwd = cwd if cwd else os.path.abspath(self.config.root_dir)

        if self.config.container_mode:
            wrapped_command = 'bash -c "{}"'.format(command)
        else:  # Docker
            self.check_docker()

            if ' ' in cwd or ' ' in self.config.build_dir:
                raise ClickableException('There are spaces in the current path, this will cause errors in the build process')

            if self.config.first_docker_info:
                logger.debug('Using docker container "{}"'.format(self.docker_image))
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

            if self.config.builder == Constants.RUST and self.config.cargo_home:
                logger.info("Caching cargo related files in {}".format(self.config.cargo_home))
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

            env_vars = self.config.prepare_docker_env_vars()

            user = ""
            if not root_user:
                user = "-u {}".format(os.getuid())

            wrapped_command = 'docker run -v {project}:{project}:Z {env} {go} {rust} {user} -w {cwd} --rm {tty} {network} -i {image} bash -c "{cmd}"'.format(
                project=cwd,
                env=env_vars,
                go=go_config,
                rust=rust_config,
                cwd=self.config.build_dir if use_build_dir else cwd,
                user=user,
                image=self.docker_image,
                cmd=command,
                tty="-t" if tty else "",
                network='--network="host"' if localhost else "",
            )

        kwargs = {}
        if use_build_dir:
            kwargs['cwd'] = self.config.build_dir

        if get_output:
            return run_subprocess_check_output(shlex.split(wrapped_command), **kwargs)
        else:
            subprocess.check_call(shlex.split(wrapped_command), **kwargs)

    def get_dependency_packages(self):
        dependencies = self.config.dependencies_host
        for dep in self.config.dependencies_target:
            if ':' in dep:
                dependencies.append(dep)
            else:
                dependencies.append('{}:{}'.format(dep, self.config.arch))
        return dependencies

    def get_ppa_adding_commands(self):
        if self.config.dependencies_ppa:
            return [
                'add-apt-repository -y {}'.format(ppa)
                for ppa in self.config.dependencies_ppa
            ]

        return []

    def construct_dockerfile_content(self, commands, env_vars):
        env_strings = [
            'ENV {}="{}"'.format(key, var) for key,var in env_vars.items()
        ]

        run_strings = [
            'RUN {}'.format(cmd) for cmd in commands
        ]

        return '''
FROM {}
{}
{}
        '''.format(
            self.base_docker_image,
            '\n'.join(env_strings),
            '\n'.join(run_strings)
        ).strip()

    def create_custom_container(self, dockerfile_content):
        if not os.path.exists(self.clickable_dir):
            os.makedirs(self.clickable_dir)

        with open(self.docker_file, 'w') as f:
            f.write(dockerfile_content)

        self.docker_image = '{}-{}'.format(self.base_docker_image, uuid.uuid4())
        with open(self.docker_name_file, 'w') as f:
            f.write(self.docker_image)

        logger.debug('Generating new docker image')
        try:
            subprocess.check_call(shlex.split('docker build -t {} .'.format(self.docker_image)), cwd=self.clickable_dir)
        except subprocess.CalledProcessError:
            self.clean_clickable()
            raise

    def is_dockerfile_outdated(self, dockerfile_content):
        if self.docker_image == self.base_docker_image:
            return True

        if not os.path.exists(self.clickable_dir):
            return True

        if not os.path.exists(self.docker_file):
            return True

        with open(self.docker_file, 'r') as f:
            if dockerfile_content.strip() != f.read().strip():
                return True

        command = 'docker images -q {}'.format(self.docker_image)
        image_exists = run_subprocess_check_output(command).strip()
        return not image_exists

    def get_apt_install_cmd(self, dependencies):
        return 'apt-get install -y --force-yes --no-install-recommends {}'.format(
                ' '.join(dependencies))

    def setup_customized_image(self):
        logger.debug('Checking dependencies and container setup')

        self.check_docker()

        commands = []
        env_vars = self.config.image_setup.get('env', {})

        commands += self.get_ppa_adding_commands()

        dependencies = self.get_dependency_packages()
        if dependencies:
            commands.append(
                'echo set debconf/frontend Noninteractive | debconf-communicate && echo set debconf/priority critical | debconf-communicate')
            commands.append(
                'apt-get update && {} && apt-get clean'.format(
                    self.get_apt_install_cmd(dependencies)))

        if self.config.image_setup:
            commands.extend(self.config.image_setup.get('run', []))

        dockerfile_content = self.construct_dockerfile_content(commands, env_vars)

        if self.is_dockerfile_outdated(dockerfile_content):
            self.create_custom_container(dockerfile_content)
        else:
            logger.debug('Image already setup')

    def setup_container_mode(self):
        ppa_commands = self.get_ppa_adding_commands()
        if ppa_commands:
            self.run_command(' && '.join(ppa_commands))

        dependencies = self.get_dependency_packages()
        if dependencies:
            self.run_command('apt-get update', use_build_dir=False)

            run = False
            for dep in dependencies:
                exists = ''
                try:
                    exists = self.run_command('dpkg -s {} | grep Status'.format(dep), get_output=True, use_build_dir=False)
                except subprocess.CalledProcessError:
                    exists = ''

                if exists.strip() != 'Status: install ok installed':
                    run = True
                    break

            if run:
                self.run_command(self.get_apt_install_cmd(dependencies),
                        use_build_dir=False)
            else:
                logger.debug('Dependencies already installed')

        if self.config.image_setup:
            for command in self.config.image_setup.get('run', []):
                self.run_command(command, use_build_dir=False)

    def needs_customized_container(self):
        return self.config.dependencies_host \
            or self.config.dependencies_target \
            or self.config.dependencies_ppa \
            or self.config.image_setup

    def check_base_image_version(self):
        if not self.minimum_version:
            return

        version = 0
        try:
            version_string = self.run_command(
                "cat /image_version",
                get_output=True,
                use_build_dir=False,
            ).strip()
            version = int(version_string)
        except ClickableException as e:
            raise e
        except Exception as e:
            logger.warn("Could not read the image version from the container")

        if version < self.minimum_version:
            raise ClickableException('This version of Clickable requires a newer version of the docker images than installed. Please run "clickable update" to update your local images.')


    def setup(self):
        if self.config.container_mode:
            self.setup_container_mode()

        if self.config.needs_clickable_image():
            self.check_base_image_version()

            if self.needs_customized_container():
                self.setup_customized_image()

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
