from .desktop import DesktopCommand
from clickable.logger import logger


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

        self.command = path_arg
        super().run()
