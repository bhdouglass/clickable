from .base import Command
from clickable.utils import print_error


class SetupLxdCommand(Command):
    aliases = ['setup_lxd']
    name = 'setup-lxd'
    help = 'Configure lxd for use with clickable'

    def run(self, path_arg=None):
        print_error('Setting up lxd is no longer supported, use docker instead')
