from .base import Command


class UpdateDockerCommand(Command):
    aliases = ['update_docker']
    name = 'update-docker'
    help = 'Update the docker container for use with clickable'
