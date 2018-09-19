from unittest import TestCase, mock

from clickable.commands.logs import LogsCommand
from ..mocks import ConfigMock, empty_fn


class TestLogsCommand(TestCase):
    def setUp(self):
        self.config = ConfigMock({})
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

    @mock.patch('clickable.commands.logs.print_warning', side_effect=empty_fn)
    def test_no_desktop_mode_logs(self, mock_print_warning):
        self.config.desktop = True
        self.command.run()

        mock_print_warning.assert_called_once()

    @mock.patch('clickable.commands.logs.print_warning', side_effect=empty_fn)
    def test_no_container_mode_logs(self, mock_print_warning):
        self.config.container_mode = True
        self.command.run()

        mock_print_warning.assert_called_once()
