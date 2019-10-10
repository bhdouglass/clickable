import subprocess
import os
import shlex

from .base import Command
from clickable.utils import (
    run_subprocess_call,
    run_subprocess_check_output,
)
from clickable.logger import logger
from clickable.exceptions import ClickableException


class ShellCommand(Command):
    aliases = ['ssh']
    name = 'shell'
    help = 'Opens a shell on the device via ssh'

    def toggle_ssh(self, on=False):
        command = 'sudo -u phablet bash -c \'/usr/bin/gdbus call -y -d com.canonical.PropertyService -o /com/canonical/PropertyService -m com.canonical.PropertyService.SetProperty ssh {}\''.format(
            'true' if on else 'false'
        )

        adb_args = ''
        if self.config.device_serial_number:
            adb_args = '-s {}'.format(self.config.device_serial_number)

        run_subprocess_call(shlex.split('adb {} shell "{}"'.format(adb_args, command)), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def run(self, path_arg=None):
        '''
        Inspired by http://bazaar.launchpad.net/~phablet-team/phablet-tools/trunk/view/head:/phablet-shell
        '''

        if self.config.ssh:
            subprocess.check_call(shlex.split('ssh phablet@{}'.format(self.config.ssh)))
        else:
            self.device.check_any_attached()

            adb_args = ''
            if self.config.device_serial_number:
                adb_args = '-s {}'.format(self.config.device_serial_number)
            else:
                self.device.check_multiple_attached()

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
                raise ClickableException('Failed to open a port to the device')

            # Purge the device host key so that SSH doesn't print a scary warning about it
            # (it changes every time the device is reflashed and this is expected)
            known_hosts = os.path.expanduser('~/.ssh/known_hosts')
            subprocess.check_call(shlex.split('touch {}'.format(known_hosts)))
            subprocess.check_call(shlex.split('ssh-keygen -f {} -R [localhost]:{}'.format(known_hosts, port)))

            id_pub = os.path.expanduser('~/.ssh/id_rsa.pub')
            if not os.path.isfile(id_pub):
                raise ClickableException('Could not find a ssh public key at "{}", please generate one and try again'.format(id_pub))

            with open(id_pub, 'r') as f:
                public_key = f.read().strip()

            self.device.run_command('[ -d ~/.ssh ] || mkdir ~/.ssh', cwd=self.config.cwd)
            self.device.run_command('touch  ~/.ssh/authorized_keys', cwd=self.config.cwd)

            output = run_subprocess_check_output('adb {} shell "grep \\"{}\\" ~/.ssh/authorized_keys"'.format(adb_args, public_key), shell=True).strip()
            if not output or 'No such file or directory' in output:
                logger.info('Inserting ssh public key on the connected device')
                self.device.run_command('echo \"{}\" >>~/.ssh/authorized_keys'.format(public_key), cwd=self.config.cwd)
                self.device.run_command('chmod 700 ~/.ssh', cwd=self.config.cwd)
                self.device.run_command('chmod 600 ~/.ssh/authorized_keys', cwd=self.config.cwd)

            subprocess.check_call(shlex.split('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -p {} phablet@localhost'.format(port)))
            self.toggle_ssh(on=False)
