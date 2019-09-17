from unittest import TestCase, mock
from unittest.mock import ANY

from clickable.commands.build_libs import LibBuildCommand
from clickable.container import Container
from ..mocks import LibConfigMock, ConfigMock, empty_fn, false_fn


class TestLibBuildCommand(TestCase):
    def setUp(self):
        self.custom_cmd = 'echo "Building lib"'
        self.config = ConfigMock()
        self.config.lib_configs = [LibConfigMock({
            'template': 'custom',
            'build': self.custom_cmd,
        })]
        self.config.container = Container(self.config)
        self.command = LibBuildCommand(self.config)

    @mock.patch('clickable.container.Container.run_command', side_effect=empty_fn)
    def test_click_build(self, mock_run_command):
        self.command.run()

        mock_run_command.assert_called_once_with(self.custom_cmd)

# TODO implement more
