import os
import subprocess

from .base import Command
from clickable.utils import print_warning, run_subprocess_check_call


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
            run_subprocess_check_call(command, cwd=cwd, shell=True)

        else:
            self.device.check_any_attached()

            if self.config.device_serial_number:
                command = 'adb -s {} push {} /home/phablet/'.format(self.config.device_serial_number, click_path)
            else:
                self.device.check_multiple_attached()
                command = 'adb push {} /home/phablet/'.format(click_path)

            run_subprocess_check_call(command, cwd=cwd, shell=True)

        self.device.run_command('pkcon install-local --allow-untrusted /home/phablet/{}'.format(click), cwd=cwd)
