from .desktop import DesktopCommand
from clickable.logger import logger
from clickable.exceptions import ClickableException
from .idedelegates.qtcreator import QtCreatorDelegate


class IdeCommand(DesktopCommand):
    aliases = []
    name = 'ide'
    help = 'Run a custom command in desktop mode (e.g. an IDE)'

    def __init__(self, config):
        super().__init__(config)
        self.custom_mode = True

    def run(self, path_arg=None):
        if not path_arg:
            raise ClickableException('No command supplied for `clickable ide`')

        #get the preprocessor according to command if any
        if 'qtcreator' in path_arg:
            self.idedelegate = QtCreatorDelegate()
            path_arg = self.idedelegate.override_command(path_arg)
            logger.info('new command: {}'.format(path_arg))

        self.command = path_arg
        super().run()
