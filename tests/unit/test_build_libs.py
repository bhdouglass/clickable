from unittest import mock
from unittest.mock import ANY

from clickable.commands.build_libs import LibBuildCommand
from .base_test import UnitTest
from ..mocks import empty_fn, false_fn


class TestLibBuildCommand(UnitTest):
    def setUp(self):
        self.custom_cmd = 'echo "Building lib"'

        config_json = {}
        config_json["libraries"] = {
            "testlib": {
                'builder': 'custom',
                'build': self.custom_cmd,
            }
        }
        self.setUpConfig(mock_config_json = config_json)
        self.command = LibBuildCommand(self.config)

    @mock.patch('clickable.container.Container.run_command', side_effect=empty_fn)
    @mock.patch('os.makedirs', side_effect=empty_fn)
    def test_click_build(self, mock_makedirs, mock_run_command):
        self.command.run()

        mock_run_command.assert_called_once_with(self.custom_cmd)
        mock_makedirs.assert_called_with(ANY, exist_ok=True)

# TODO implement more
