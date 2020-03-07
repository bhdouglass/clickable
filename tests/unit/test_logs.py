from unittest import mock
from unittest.mock import ANY

from clickable.commands.logs import LogsCommand
from ..mocks import empty_fn, true_fn
from .base_test import UnitTest


class TestLogsCommand(UnitTest):
    def setUp(self):
        self.setUpConfig()
        self.command = LogsCommand(self.config)

    @mock.patch('clickable.device.Device.run_command', side_effect=empty_fn)
    def test_logs(self, mock_run_command):
        self.command.run()

        mock_run_command.assert_called_once_with('tail -f ~/.cache/upstart/application-click-foo.bar_foo_1.2.3.log')

    @mock.patch('clickable.device.Device.run_command', side_effect=empty_fn)
    def test_custom_log_file(self, mock_run_command):
        self.config.log = 'foo.log'
        self.command.run()

        mock_run_command.assert_called_once_with('tail -f foo.log')

    @mock.patch('clickable.config.config.Config.is_desktop_mode', side_effect=true_fn)
    @mock.patch('clickable.commands.logs.logger.debug', side_effect=empty_fn)
    def test_no_desktop_mode_logs(self, mock_logger_debug, mock_desktop_mode):
        self.command.run()

        mock_logger_debug.assert_called_once_with(ANY)
        mock_desktop_mode.assert_called_once_with()

    @mock.patch('clickable.commands.logs.logger.debug', side_effect=empty_fn)
    def test_no_container_mode_logs(self, mock_logger_debug):
        self.config.container_mode = True
        self.command.run()

        mock_logger_debug.assert_called_once_with(ANY)
