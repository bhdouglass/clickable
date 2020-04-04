import os

from clickable.commands.docker.docker_config import DockerConfig
from clickable.utils import makedirs
from clickable.config.constants import Constants
from .docker_support import DockerSupport


class ThemeSupport(DockerSupport):
    config = None
    package_name = ''

    def __init__(self, config):
        self.config = config

    def update(self, docker_config: DockerConfig):
        package_name = self.config.install_files.find_package_name()

        config_path = makedirs(os.path.join(Constants.desktop_device_home, '.config/ubuntu-ui-toolkit'))

        theme = 'Ubuntu.Components.Themes.Ambiance'
        if self.config.dark_mode:
            theme = 'Ubuntu.Components.Themes.SuruDark'

        with open(os.path.join(config_path, 'theme.ini'), 'w') as f:
            f.write('[General]\ntheme=' + theme)
