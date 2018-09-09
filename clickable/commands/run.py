from .base import Command


class RunCommand(Command):
    aliases = []
    name = 'run'
    help = 'Runs an arbitrary command in the clickable container'

    def run(self, path_arg=None):
        if not path_arg:
            raise ValueError('No command supplied for `clickable run`')


        self.container.setup_dependencies()
        self.container.run_command(path_arg, use_dir=False)
