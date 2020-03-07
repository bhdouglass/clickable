from .base import Command
from clickable.logger import logger


class LogCommand(Command):
    aliases = []
    name = 'log'
    help = 'Outputs the app\'s log from the device'

    def run(self, path_arg=None):
        if self.config.is_desktop_mode():
            logger.debug('Skipping log, running in desktop mode')
            return
        elif self.config.container_mode:
            logger.debug('Skipping log, running in container mode')
            return

        log = '~/.cache/upstart/application-click-{}.log'.format(
            self.config.install_files.find_full_package_name(),
        )

        if self.config.log:
            log = self.config.log

        self.device.run_command('cat {}'.format(log))
