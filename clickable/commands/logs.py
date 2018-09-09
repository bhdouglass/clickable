from .base import Command
from clickable.utils import print_warning


class LogsCommand(Command):
    aliases = ['log']
    name = 'logs'
    help = 'Follow the apps log file on the device'

    def run(self, path_arg=None):
        if self.config.desktop:
            print_warning('Skipping logs, running in desktop mode')
            return
        elif self.config.container_mode:
            print_warning('Skipping logs, running in container mode')
            return

        log = '~/.cache/upstart/application-click-{}_{}_{}.log'.format(
            self.config.find_package_name(),
            self.config.find_app_name(),
            self.config.find_version()
        )

        if self.config.log:
            log = self.config.log

        self.device.run_command('tail -f {}'.format(log))
