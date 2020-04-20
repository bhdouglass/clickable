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

        log = '~/.cache/upstart/application-click-{}.log'.format(
            self.config.install_files.find_full_package_name(),
        )

        if self.config.log:
            log = self.config.log

        self.device.run_command('tail -f {}'.format(log))
