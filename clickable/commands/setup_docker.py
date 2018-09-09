from .base import Command


class SetupDockerCommand(Command):
    aliases = ['setup_docker']
    name = 'setup-docker'
    help = 'Configure docker for use with clickable'
