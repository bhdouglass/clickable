from .base import Command
from clickable.logger import logger


class WritableImageCommand(Command):
    aliases = ['writable_image', 'writeable-image']
    name = 'writable-image'
    help = 'Make your Ubuntu Touch device\'s rootfs writable'

    def run(self, path_arg=None):
        command = 'dbus-send --system --print-reply --dest=com.canonical.PropertyService /com/canonical/PropertyService com.canonical.PropertyService.SetProperty string:writable boolean:true'
        self.device.run_command(command, cwd=self.config.cwd)
        logger.info('Rebooting device for writable image')
