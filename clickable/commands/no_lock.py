from .base import Command
from clickable.logger import logger


class NoLockCommand(Command):
    aliases = ['no_lock']
    name = 'no-lock'
    help = 'Turns off the device’s display timeout'

    def run(self, path_arg=None):
        logger.info('Turning off device activity timeout')
        command = 'gsettings set com.ubuntu.touch.system activity-timeout 0'
        self.device.run_command(command, cwd=self.config.cwd)
