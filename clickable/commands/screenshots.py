from .base import Command
from clickable.utils import run_subprocess_check_call


class WritableImageCommand(Command):
    aliases = []
    name = 'screenshots'
    help = 'Download all the screenshots from the device'

    def run(self, path_arg=None):
        command = 'adb pull /home/phablet/Pictures/Screenshots'
        run_subprocess_check_call(command, cwd=self.config.cwd)
