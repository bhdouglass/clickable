from .base import Command
from clickable.logger import logger


class ClickBuildCommand(Command):
    aliases = ['build_click', 'build-click', 'click_build']
    name = 'click-build'
    help = 'Deprecated'

    def run(self, path_arg=None):
        logger.warning('The click-build command has been merged into the build command. Please remove this command from your CI, as this warning will be removed in a future version.')
