import os
import subprocess

from .base import Command
from clickable.utils import (
    check_any_devices,
    run_device_command,
    print_warning,
    check_multiple_devices,
)


class InstallCommand(Command):
    aliases = []
    name = 'install'
    help = 'Takes a built click package and installs it on a device'

    def run(self, path_arg=None):
        if self.config.desktop:
            print_warning('Skipping install, running in desktop mode')
            return
        elif self.config.container_mode:
            print_warning('Skipping install, running in container mode')
            return

        cwd = '.'
        if path_arg:
            click = os.path.basename(path_arg)
            click_path = path_arg
        else:
            click = '{}_{}_{}.click'.format(self.config.find_package_name(), self.config.find_version(), self.config.arch)
            click_path = os.path.join(self.config.dir, click)
            cwd = self.config.dir

        if self.config.ssh:
            command = 'scp {} phablet@{}:/home/phablet/'.format(click_path, self.config.ssh)
            subprocess.check_call(command, cwd=cwd, shell=True)

        else:
            check_any_devices()

            if self.config.device_serial_number:
                command = 'adb -s {} push {} /home/phablet/'.format(self.config.device_serial_number, click_path)
            else:
                check_multiple_devices(self.config.device_serial_number)
                command = 'adb push {} /home/phablet/'.format(click_path)
            subprocess.check_call(command, cwd=cwd, shell=True)

        run_device_command('pkcon install-local --allow-untrusted /home/phablet/{}'.format(click), self.config, cwd=cwd)
