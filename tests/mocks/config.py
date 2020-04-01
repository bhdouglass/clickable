from clickable.config.project import ProjectConfig
from clickable.config.constants import Constants
from clickable.config.file_helpers import InstallFiles
from unittest.mock import Mock


class InstallFilesMock(InstallFiles):
    def write_manifest(self, *args):
        pass

    def get_manifest(self):
        return {
            'version': '1.2.3',
            'name': 'foo.bar',
            'architecture': '@CLICK_ARCH@',
            'hooks': {
                'foo': {
                    'desktop': '/fake/foo.desktop',
                },
            },
        }


class ConfigMock(ProjectConfig):
    def __init__(self,
                 mock_config_json=None,
                 mock_config_env=None,
                 mock_install_files=False,
                 *args, **kwargs):
        self.mock_config_json = mock_config_json
        self.mock_config_env = mock_config_env
        self.mock_install_files = mock_install_files
        super().__init__(clickable_version='0.0.0', *args, **kwargs)

    def load_json_config(self, config_path):
        if self.mock_config_json is None:
            return super().load_json_config(config_path)
        else:
            config_json = self.mock_config_json
            return config_json

    def get_env_var(self, key):
        if self.mock_config_env is None:
            return super().get_env_var(key)
        else:
            return self.mock_config_env.get(key, None)

    def set_template_interactive(self):
        if not self.config['template']:
            self.config["template"] = Constants.PURE

    def setup_helpers(self):
        super().setup_helpers()
        if self.mock_install_files:
            self.install_files = InstallFilesMock(
                    self.config['install_dir'],
                    self.config['template'],
                    self.config['arch'])
