from .base import Command
from clickable.logger import logger


class DevicesCommand(Command):
    aliases = []
    name = 'devices'
    help = 'Lists all connected devices'

    def run(self, path_arg=None):
        devices = self.device.detect_attached()

        if len(devices) == 0:
            logger.warning('No attached devices')
        else:
            for device in devices:
                logger.info(device)
