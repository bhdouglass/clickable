from .base import Command
from clickable.utils import print_info, run_device_command


class NoLockCommand(Command):
    aliases = ['no_lock']
    name = 'no-lock'
    help = 'Turns off the device’s display timeout'

    def run(self, path_arg=None):
        print_info('Turning off device activity timeout')
        command = 'gsettings set com.ubuntu.touch.system activity-timeout 0'
        run_device_command(command, self.config, cwd=self.config.cwd)
