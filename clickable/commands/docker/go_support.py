from clickable import Config
from clickable.commands.docker.docker_config import DockerConfig
from .docker_support import DockerSupport


class GoSupport(DockerSupport):
    config = None

    def __init__(self, config: Config):
        self.config = config

    def update(self, docker_config: DockerConfig):
        template = self.config.config['template']

        if template == Config.GO:
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
