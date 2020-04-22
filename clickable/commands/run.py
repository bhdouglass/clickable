from .base import Command
from clickable.exceptions import ClickableException


class RunCommand(Command):
    aliases = []
    name = 'run'
    help = 'Runs an arbitrary command in the clickable container'

    def run(self, path_arg=None):
        if not path_arg:
            raise ClickableException('No command supplied for `clickable run`')

        self.config.container.setup()
        self.config.container.run_command(path_arg,
            use_build_dir=False,
            tty=True,
            localhost=True,
        )
