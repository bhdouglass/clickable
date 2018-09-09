import subprocess
import os
import shlex

from .base import Command
from clickable.utils import (
    run_subprocess_call,
    run_subprocess_check_output,
    check_any_devices,
    check_multiple_devices,
    run_device_command,
)


class ShellCommand(Command):
    aliases = []
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
            check_any_devices()

            adb_args = ''
            if self.config.device_serial_number:
                adb_args = '-s {}'.format(self.config.device_serial_number)
            else:
                check_multiple_devices(self.config.device_serial_number)

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

            run_device_command('[ -d ~/.ssh ] || mkdir ~/.ssh', self.config, cwd=self.config.cwd)
            run_device_command('touch  ~/.ssh/authorized_keys', self.config, cwd=self.config.cwd)

            output = run_subprocess_check_output('adb {} shell "grep \\"{}\\" ~/.ssh/authorized_keys"'.format(adb_args, public_key), shell=True).strip()
            if not output or 'No such file or directory' in output:
                print_info('Inserting ssh public key on the connected device')
                run_device_command('echo \"{}\" >>~/.ssh/authorized_keys'.format(public_key), self.config, cwd=self.config.cwd)
                run_device_command('chmod 700 ~/.ssh', self.config, cwd=self.config.cwd)
                run_device_command('chmod 600 ~/.ssh/authorized_keys', self.config, cwd=self.config.cwd)

            subprocess.check_call(shlex.split('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -p {} phablet@localhost'.format(port)))
            self.toggle_ssh(on=False)
