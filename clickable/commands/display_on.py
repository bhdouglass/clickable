from .base import Command
from clickable.utils import run_device_command


class DisplayOnCommand(Command):
    aliases = ['display_on']
    name = 'display-on'
    help = 'Turns on the device’s display and keeps it on until you hit CTRL+C'

    def run(self, path_arg=None):
        run_device_command('powerd-cli display on', self.config, cwd=self.config.cwd)
