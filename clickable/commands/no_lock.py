from .base import Command
from clickable.utils import print_info


class NoLockCommand(Command):
    aliases = ['no_lock']
    name = 'no-lock'
    help = 'Turns off the device’s display timeout'
    skip_auto_detect = True

    def run(self, path_arg=None):
        print_info('Turning off device activity timeout')
        command = 'gsettings set com.ubuntu.touch.system activity-timeout 0'
        self.device.run_command(command, cwd=self.config.cwd)
