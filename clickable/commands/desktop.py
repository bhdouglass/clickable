import os
import shlex
import subprocess
from pathlib import Path

from clickable.utils import (
    check_command,
    is_command,
    makedirs,
    try_find_locale,
    run_subprocess_check_output,
)
from clickable.logger import logger
from clickable.exceptions import ClickableException
from .base import Command
from .build import BuildCommand
from .clean import CleanCommand
from .docker.debug_gdb_support import DebugGdbSupport
from .docker.docker_config import DockerConfig
from .docker.go_support import GoSupport
from .docker.nvidia_support import NvidiaSupport
from .docker.rust_support import RustSupport
from .docker.webapp_support import WebappSupport
from .docker.theme_support import ThemeSupport
from .docker.multimedia_support import MultimediaSupport


class DesktopCommand(Command):
    aliases = []
    name = 'desktop'
    help = 'Run the app on your desktop'

    def run(self, path_arg=None):
        self.prepare_run()
        self.run_app()

    def prepare_run(self):
        if not self.config.desktop_skip_build:
            if not self.config.dirty:
                CleanCommand(self.config).run()
            BuildCommand(self.config).run()

    def setup_docker(self):
        self.config.container.check_docker()
        if is_command('xhost'):
            subprocess.check_call(shlex.split('xhost +local:docker'))
        else:
            logger.warning('xhost not installed, desktop mode may fail')

        return self.setup_docker_config()

    def setup_docker_config(self):
        docker_config = DockerConfig()

        docker_config.uid = os.getuid()
        docker_config.docker_image = self.config.container.docker_image
        docker_config.working_directory = self.config.install_dir
        docker_config.use_nvidia = self.config.use_nvidia

        docker_config.execute = self.determine_executable(
            self.find_desktop_file()
        )

        package_name = self.config.find_package_name()

        docker_config.add_volume_mappings(
            self.setup_volume_mappings(package_name)
        )

        docker_config.add_environment_variables(
            self.setup_environment(docker_config.working_directory)
        )

        NvidiaSupport().update(docker_config)

        WebappSupport(package_name).update(docker_config)

        GoSupport(self.config).update(docker_config)

        RustSupport(self.config).update(docker_config)

        DebugGdbSupport(self.config).update(docker_config)

        ThemeSupport(self.config).update(docker_config)

        MultimediaSupport(self.config).update(docker_config)

        return docker_config

    def find_desktop_file(self):
        desktop_path = None
        hooks = self.config.get_manifest().get('hooks', {})
        try:
            app = self.config.find_app_name()
            if app in hooks and 'desktop' in hooks[app]:
                desktop_path = hooks[app]['desktop']
        except ClickableException:
            for key, value in hooks.items():
                if 'desktop' in value:
                    desktop_path = value['desktop']
                    break

        if not desktop_path:
            raise ClickableException('Could not find desktop file for app')

        desktop_path = os.path.join(self.config.install_dir, desktop_path)
        if not os.path.exists(desktop_path):
            raise ClickableException('Could not determine executable. Desktop file does not exist: "{}"'.format(desktop_path))

        return desktop_path

    def determine_executable(self, desktop_path):
        execute = None
        with open(desktop_path, 'r') as desktop_file:
            for line in desktop_file.readlines():
                if line.startswith('Exec='):
                    execute = line
                    break

        if not execute:
            raise ClickableException('No "Exec" line found in the desktop file {}'.format(desktop_path))

        return execute[len('Exec='):].strip()

    def get_time_zone(self):
        try:
            return run_subprocess_check_output('timedatectl show -p Timezone --value')
        except:
            pass

        if os.path.exists('/etc/timezone'):
            with open('/etc/timezone') as host_timezone_file:
                return host_timezone_file.readline().strip()

        try:
            output = run_subprocess_check_output('timedatectl status')
            for line in output.splitlines():
                line = line.strip()
                if line.startswith('Time zone:'):
                    start = line.find(':') + 1
                    end = line.find('(')
                    return line[start:end].strip()
        except:
            pass

        return 'UTC'

    def setup_environment(self, working_directory):
        lib_path = self.get_docker_lib_path_env(working_directory)

        return {
            'LANG': self.config.desktop_locale,
            'LANGUAGE': self.config.desktop_locale,
            'LC_CTYPE': self.config.desktop_locale,
            'LC_NUMERIC': self.config.desktop_locale,
            'LC_TIME': self.config.desktop_locale,
            'LC_COLLATE': self.config.desktop_locale,
            'LC_MONETARY': self.config.desktop_locale,
            'LC_MESSAGES': self.config.desktop_locale,
            'LC_PAPER': self.config.desktop_locale,
            'LC_NAME': self.config.desktop_locale,
            'LC_ADDRESS': self.config.desktop_locale,
            'LC_TELEPHONE': self.config.desktop_locale,
            'LC_MEASUREMENT': self.config.desktop_locale,
            'LC_IDENTIFICATION': self.config.desktop_locale,
            'LC_ALL': self.config.desktop_locale,
            'TZ': self.get_time_zone(),
            'APP_DIR': self.config.install_dir,
            'TEXTDOMAINDIR': try_find_locale(self.config.install_dir),
            'XAUTHORITY': '/tmp/.docker.xauth',
            'DISPLAY': os.environ['DISPLAY'],
            'QML2_IMPORT_PATH': lib_path,
            'LD_LIBRARY_PATH': lib_path,
            'PATH': self.get_docker_path_env(working_directory),
            'HOME': '/home/phablet',
            'OXIDE_NO_SANDBOX': '1',
            'UBUNTU_APP_LAUNCH_ARCH': 'x86_64-linux-gnu',
        }

    def get_docker_lib_path_env(self, working_directory):
        return ':'.join([
            os.path.join(working_directory, 'lib/x86_64-linux-gnu'),
            os.path.join(working_directory, 'lib'),
            '/usr/local/nvidia/lib',
            '/usr/local/nvidia/lib64',
        ])

    def get_docker_path_env(self, working_directory):
        return ':'.join([
            os.path.join(working_directory, 'bin'),
            os.path.join(working_directory, 'lib/x86_64-linux-gnu/bin'),
            working_directory,
            '/usr/local/nvidia/bin',
            '/bin',
            '/usr/bin',
        ])

    def setup_volume_mappings(self, package_name):
        xauth_path = self.touch_xauth()

        device_home = self.config.desktop_device_home
        makedirs(device_home)
        logger.info("Mounting device home to {}".format(device_home))

        return {
            self.config.cwd: self.config.cwd,
            '/tmp/.X11-unix': '/tmp/.X11-unix',
            xauth_path: xauth_path,
            device_home: '/home/phablet',
        }

    def touch_xauth(self):
        xauth_path = '/tmp/.docker.xauth'
        Path(xauth_path).touch()
        return xauth_path

    def run_app(self):
        docker_config = self.setup_docker()
        command = docker_config.render_command()
        logger.debug(command)

        subprocess.check_call(shlex.split(command), cwd=docker_config.working_directory)
