from .base import Command
from clickable.utils import print_info, print_warning


class DevicesCommand(Command):
    aliases = []
    name = 'devices'
    help = 'Lists all connected devices'
    skip_auto_detect = True

    def run(self, path_arg=None):
        devices = self.device.detect_attached()

        if len(devices) == 0:
            print_warning('No attached devices')
        else:
            for device in devices:
                print_info(device)
