from .base import Command
from clickable.utils import (
    print_info,
    print_warning,
    detect_devices,
)


class DevicesCommand(Command):
    aliases = []
    name = 'devices'
    help = 'Lists all connected devices'

    def run(self, path_arg=None):
        devices = detect_devices()

        if len(devices) == 0:
            print_warning('No attached devices')
        else:
            for device in devices:
                print_info(device)
