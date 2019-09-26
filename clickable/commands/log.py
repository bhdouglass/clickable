from .base import Command
from clickable.logger import logger


class LogCommand(Command):
    aliases = []
    name = 'log'
    help = 'Outputs the app\'s log from the device'

    def run(self, path_arg=None):
        if self.config.desktop:
            logger.debug('Skipping log, running in desktop mode')
            return
        elif self.config.container_mode:
            logger.debug('Skipping log, running in container mode')
            return

        log = '~/.cache/upstart/application-click-{}_{}_{}.log'.format(
            self.config.find_package_name(),
            self.config.find_app_name(),
            self.config.find_version()
        )

        if self.config.log:
            log = self.config.log

        self.device.run_command('cat {}'.format(log))
