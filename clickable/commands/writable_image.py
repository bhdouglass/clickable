from .base import Command
from clickable.utils import print_info, run_device_command


class WritableImageCommand(Command):
    aliases = ['writable_image']
    name = 'writable-image'
    help = 'Make your Ubuntu Touch device\'s rootfs writable'

    def run(self, path_arg=None):
        command = 'dbus-send --system --print-reply --dest=com.canonical.PropertyService /com/canonical/PropertyService com.canonical.PropertyService.SetProperty string:writable boolean:true'
        run_device_command(command, self.config, cwd=self.config.cwd)
        print_info('Rebooting for writable image')
