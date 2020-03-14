from .clean import CleanCommand
from .build import BuildCommand
from clickable.logger import logger


class CleanBuildCommand(CleanCommand, BuildCommand):
    aliases = []
    name = 'clean-build'
    help = 'Clean the build directory before compiling the app'

    def run(self, path_arg=None):
        CleanCommand.run(self, path_arg)
        BuildCommand.run(self, path_arg)
