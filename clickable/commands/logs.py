from .base import Command
from clickable.logger import logger


class LogsCommand(Command):
    aliases = []
    name = 'logs'
    help = 'Follow the app\'s log file on the device'

    def run(self, path_arg=None):
        if self.config.is_desktop_mode():
            logger.debug('Skipping logs, running in desktop mode')
            return
        elif self.config.container_mode:
            logger.debug('Skipping logs, running in container mode')
            return

        log = '~/.cache/upstart/application-click-{}_{}_{}.log'.format(
            self.config.find_package_name(),
            self.config.find_app_name(),
            self.config.find_version()
        )

        if self.config.log:
            log = self.config.log

        self.device.run_command('tail -f {}'.format(log))
