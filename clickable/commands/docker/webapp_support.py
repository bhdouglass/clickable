from clickable.commands.docker.docker_config import DockerConfig
from .docker_support import DockerSupport


class WebappSupport(DockerSupport):
    package_name = ''

    def __init__(self, package_name):
        self.package_name = package_name

    def update(self, docker_config: DockerConfig):
        # changes docker config if Exec=webapp-container
        if self.is_executable_webapp_container(docker_config):
            docker_config.add_environment_variables({'APP_ID': self.package_name})

    def is_executable_webapp_container(self, docker_config):
        return docker_config.execute.startswith('webapp-container')
