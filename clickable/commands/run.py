from .base import Command
from clickable.exceptions import ClickableException


class RunCommand(Command):
    aliases = []
    name = 'run'
    help = 'Runs an arbitrary command in the clickable container'

    def run(self, path_arg=None):
        cmd = path_arg
        if not cmd:
            cmd = "bash"

        self.config.container.setup()
        self.config.container.run_command(
            cmd,
            use_build_dir=False,
            tty=True,
            localhost=True,
            root_user=True,
        )
