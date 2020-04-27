from clickable import ProjectConfig
from clickable.config.constants import Constants
from clickable.commands.docker.docker_config import DockerConfig
from .docker_support import DockerSupport


class GoSupport(DockerSupport):
    config = None

    def __init__(self, config: ProjectConfig):
        self.config = config

    def update(self, docker_config: DockerConfig):
        builder = self.config.builder

        if builder == Constants.GO:
            go_paths = list(map(
                lambda gopath:
                '/gopath/path{}'.format(gopath),
                self.config.gopath.split(':')
            ))

            for path in go_paths:
                docker_config.add_volume_mappings({
                    path: path
                })

            docker_config.add_environment_variables({
                'GOPATH': ':'.join(list(go_paths))
            })
