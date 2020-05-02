import os
import subprocess

from .base import Command
from clickable.utils import run_subprocess_check_call
from clickable.logger import logger


class InstallCommand(Command):
    aliases = []
    name = 'install'
    help = 'Takes a built click package and installs it on a device'

    def try_find_installed_version(self, package_name):
        try:
            response = self.device.run_command('readlink /opt/click.ubuntu.com/{}/current'.format(package_name), get_output=True)
            return response.splitlines()[-1]
        except:
            return None

    def try_uninstall(self):
        package_name = self.config.install_files.find_package_name()
        version = self.try_find_installed_version(package_name)

        if version:
            self.device.run_command('pkcon remove \\"{};{};all;local:click\\"'.format(package_name, version))

    def run(self, path_arg=None):
        if self.config.is_desktop_mode():
            logger.debug('Skipping install, running in desktop mode')
            return
        elif self.config.container_mode:
            logger.debug('Skipping install, running in container mode')
            return

        cwd = '.'
        if path_arg:
            click = os.path.basename(path_arg)
            click_path = path_arg
        else:
            click = self.config.install_files.get_click_filename()
            click_path = os.path.join(self.config.build_dir, click)
            cwd = self.config.build_dir

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

        if path_arg:
            logger.info("Skipping uninstall step, because you specified a click package.")
        else:
            self.try_uninstall()

        self.device.run_command('pkcon install-local --allow-untrusted /home/phablet/{}'.format(click), cwd=cwd)
        self.device.run_command('rm /home/phablet/{}'.format(click), cwd=cwd)
