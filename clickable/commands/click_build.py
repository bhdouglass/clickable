from .base import Command
from clickable.utils import print_warning


class ClickBuildCommand(Command):
    aliases = ['build_click', 'build-click', 'click_build']
    name = 'click-build'
    help = 'Deprecated'

    def run(self, path_arg=None):
        print_warning('The click-build command has been merged into the build command. Please remove this command from your CI, as this warning will be removed in a future version.')
