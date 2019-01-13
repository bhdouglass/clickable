import os
import subprocess
import shlex

from .base import Command
from .clean import CleanCommand
from .build import BuildCommand
from clickable.utils import (
    check_command,
    print_warning,
)
from clickable.config import Config


class DesktopCommand(Command):
    aliases = []
    name = 'desktop'
    help = 'Run the app on your desktop'

    def run(self, path_arg=None):
        if self.config.lxd:
            raise Exception('Using lxd for desktop mode is not supported')

        if not self.config.dirty:
            clean = CleanCommand(self.config)
            clean.run()
        build = BuildCommand(self.config)
        build.run()

        desktop_path = None
        hooks = self.config.get_manifest().get('hooks', {})
        app = self.config.find_app_name()
        if app:
            if app in hooks and 'desktop' in hooks[app]:
                desktop_path = hooks[app]['desktop']
        else:
            for key, value in hooks.items():
                if 'desktop' in value:
                    desktop_path = value['desktop']
                    break

        if not desktop_path:
            raise Exception('Could not find desktop file for app "{}"'.format(app))

        desktop_path = os.path.join(self.config.temp, desktop_path)
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

        self.container.check_docker()

        share = '/tmp/clickable/share'
        if not os.path.isdir(share):
            os.makedirs(share)

        cache = '/tmp/clickable/cache'
        if not os.path.isdir(cache):
            os.makedirs(cache)

        config = '/tmp/clickable/config'
        if not os.path.isdir(config):
            os.makedirs(config)

        volumes = '-v {}:{} -v /tmp/.X11-unix:/tmp/.X11-unix -v {}:{} -v {}:/home/phablet/.local/share -v {}:/home/phablet/.cache -v {}:/home/phablet/.config'.format(
            self.config.cwd,
            self.config.cwd,
            xauth,
            xauth,
            share,
            cache,
            config,
        )

        if self.config.use_nvidia:
            volumes += ' -v /dev/snd/pcmC2D0c:/dev/snd/pcmC2D0c -v /dev/snd/controlC2:/dev/snd/controlC2 --device /dev/snd'

        lib_path = ':'.join([
            os.path.join(self.config.temp, 'lib/x86_64-linux-gnu'),
            os.path.join(self.config.temp, 'lib'),
            '/usr/local/nvidia/lib',
            '/usr/local/nvidia/lib64',
        ])

        path = ':'.join([
            '/usr/local/nvidia/bin',
            '/bin',
            '/usr/bin',
            os.path.join(self.config.temp, 'bin'),
            os.path.join(self.config.temp, 'lib/x86_64-linux-gnu/bin'),
            self.config.temp,
        ])
        environment = '-e XAUTHORITY=/tmp/.docker.xauth -e DISPLAY={} -e QML2_IMPORT_PATH={} -e LD_LIBRARY_PATH={} -e PATH={} -e HOME=/home/phablet -e OXIDE_NO_SANDBOX=1'.format(
            os.environ['DISPLAY'],
            lib_path,
            lib_path,
            path,
        )

        if execute.startswith('webapp-container'):
            # This is needed for the webapp-container, so only do it for this case
            volumes = '{} -v /etc/passwd:/etc/passwd'.format(volumes)
            environment = '{} -e APP_ID={}'.format(environment, self.config.find_package_name())

        go_config = ''
        if self.config.gopath:
            go_config = '-v {}:/gopath -e GOPATH=/gopath'.format(self.config.gopath)

        rust_config = ''

        if self.config.config['template'] == Config.RUST and self.config.cargo_home:
            rust_config = '-v {}:/opt/rust/cargo/registry -v {}:/opt/rust/cargo/git'.format(
                os.path.join(self.config.cargo_home, 'registry'),
                os.path.join(self.config.cargo_home, 'git'),
            )

        run_xhost = False
        try:
            check_command('xhost')
            run_xhost = True
        except Exception:  # TODO catch a specific Exception
            print_warning('xhost not installed, desktop mode may fail')
            run_xhost = False

        if run_xhost:
            subprocess.check_call(shlex.split('xhost +local:docker'))

        command = '{} run {} {} {} {} -w {} -u {} --rm -i {} bash -c "{}"'.format(
            'nvidia-docker' if self.config.use_nvidia else 'docker',
            volumes,
            go_config,
            rust_config,
            environment,
            self.config.temp,
            os.getuid(),
            self.container.docker_image,
            execute,
        )

        subprocess.check_call(shlex.split(command), cwd=self.config.temp)
