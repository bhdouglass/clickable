from unittest import TestCase, mock
from unittest.mock import ANY

from clickable.commands.launch import LaunchCommand
from ..mocks import ConfigMock, empty_fn, exception_fn


class TestLaunchCommand(TestCase):
    def setUp(self):
        self.config = ConfigMock()
        self.command = LaunchCommand(self.config)

    @mock.patch('clickable.device.Device.run_command', side_effect=empty_fn)
    def test_kill(self, mock_run_command):
        self.config.kill = 'foo and bar'
        self.command.kill()

        mock_run_command.assert_called_once_with('pkill -f \\"[f]oo and bar\\"')

    @mock.patch('clickable.device.Device.run_command', side_effect=exception_fn)
    def test_kill_ignores_exceptions(self, mock_run_command):
        self.config.kill = 'foo and bar'
        self.command.kill()

    @mock.patch('clickable.commands.launch.print_warning', side_effect=empty_fn)
    def test_kill_skips_desktop(self, mock_print_warning):
        self.config.desktop = True
        self.command.kill()

        mock_print_warning.assert_called_once_with(ANY)

    @mock.patch('clickable.commands.launch.print_warning', side_effect=empty_fn)
    def test_kill_skips_container_mode(self, mock_print_warning):
        self.config.container_mode = True
        self.command.kill()

        mock_print_warning.assert_called_once_with(ANY)

    @mock.patch('clickable.device.Device.run_command', side_effect=empty_fn)
    def test_launch(self, mock_run_command):
        self.command.run()

        mock_run_command.assert_called_once_with('sleep 1s && ubuntu-app-launch foo.bar_foo_1.2.3', cwd='/tmp/build')

    @mock.patch('clickable.device.Device.run_command', side_effect=empty_fn)
    def test_launch_path_arg(self, mock_run_command):
        self.command.run('foo')

        mock_run_command.assert_called_once_with('sleep 1s && ubuntu-app-launch foo', cwd='.')

    @mock.patch('clickable.device.Device.run_command', side_effect=empty_fn)
    def test_launch_custom(self, mock_run_command):
        self.config.launch = 'foo'
        self.command.run()

        mock_run_command.assert_called_once_with('sleep 1s && foo', cwd='/tmp/build')
