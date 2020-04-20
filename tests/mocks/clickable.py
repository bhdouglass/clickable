from clickable import Clickable
from ..mocks import ConfigMock
import os

class ClickableMock(Clickable):
    def __init__(self,
                 mock_config_json=None,
                 mock_config_env=None,
                 mock_install_files=False):
        self.mock_config_json = mock_config_json
        self.mock_config_env = mock_config_env
        self.mock_install_files = mock_install_files
        super().__init__()

    def setup_config(self, args, commands):
        container_mode_key = "CLICKABLE_CONTAINER_MODE"

        if (self.mock_config_env is not None and
                not container_mode_key in self.mock_config_env and
                container_mode_key in os.environ):
            self.mock_config_env[container_mode_key] = os.environ[container_mode_key]

        return ConfigMock(
            args=args,
            commands=commands,
            mock_config_json=self.mock_config_json,
            mock_config_env=self.mock_config_env,
            mock_install_files=self.mock_install_files,
        )

    def run_clickable(self, cli_args=[]):
        parser = Clickable.create_parser("Integration Test Call")
        run_args = parser.parse_args(cli_args)
        self.run(run_args.commands, run_args)
