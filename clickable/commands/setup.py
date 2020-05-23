from .base import Command
from clickable.logger import logger
from clickable.exceptions import ClickableException


class SetupCommand(Command):
    aliases = []
    name = 'setup'
    help = 'Setup docker initially'

    def run(self, path_arg=None):
        try:
            self.config.container.run_command("echo ''", use_build_dir=False)
            logger.info('Clickable is set up and ready.')
        except ClickableException:
            logger.warning('Please log out or restart to apply changes')
