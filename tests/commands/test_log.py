from unittest import TestCase, mock
from unittest.mock import ANY

from clickable.commands.log import LogCommand
from ..mocks import ConfigMock, empty_fn


class TestLogCommand(TestCase):
    def setUp(self):
        self.config = ConfigMock()
        self.command = LogCommand(self.config)

    @mock.patch('clickable.device.Device.run_command', side_effect=empty_fn)
    def test_log(self, mock_run_command):
        self.command.run()

        mock_run_command.assert_called_once_with('cat ~/.cache/upstart/application-click-foo.bar_foo_1.2.3.log')

    @mock.patch('clickable.device.Device.run_command', side_effect=empty_fn)
    def test_custom_log_file(self, mock_run_command):
        self.config.log = 'foo.log'
        self.command.run()

        mock_run_command.assert_called_once_with('cat foo.log')

    @mock.patch('clickable.commands.log.print_warning', side_effect=empty_fn)
    def test_no_desktop_mode_log(self, mock_print_warning):
        self.config.desktop = True
        self.command.run()

        mock_print_warning.assert_called_once_with(ANY)

    @mock.patch('clickable.commands.log.print_warning', side_effect=empty_fn)
    def test_no_container_mode_log(self, mock_print_warning):
        self.config.container_mode = True
        self.command.run()

        mock_print_warning.assert_called_once_with(ANY)
