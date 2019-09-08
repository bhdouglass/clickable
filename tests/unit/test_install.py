from unittest import TestCase, mock
from unittest.mock import ANY

from clickable.commands.install import InstallCommand
from clickable.container import Container
from ..mocks import ConfigMock, empty_fn


class TestInstallCommand(TestCase):
    def setUp(self):
        self.config = ConfigMock()
        self.config.container = Container(self.config)
        self.command = InstallCommand(self.config)

    @mock.patch('clickable.device.Device.check_any_attached', side_effect=empty_fn)
    @mock.patch('clickable.device.Device.check_multiple_attached', side_effect=empty_fn)
    @mock.patch('clickable.device.Device.run_command', side_effect=empty_fn)
    @mock.patch('clickable.commands.install.run_subprocess_check_call', side_effect=empty_fn)
    def test_install_adb(self, mock_run_subprocess_check_call, mock_run_command, mock_check_multiple_attached, mock_check_any_attached):
        self.command.run()

        mock_check_any_attached.assert_called_once_with()
        mock_check_multiple_attached.assert_called_once_with()
        mock_run_subprocess_check_call.assert_called_once_with('adb push /tmp/build/foo.bar_1.2.3_armhf.click /home/phablet/', cwd='/tmp/build', shell=True)
        mock_run_command.assert_called_once_with(ANY, cwd='/tmp/build')

    @mock.patch('clickable.device.Device.check_any_attached', side_effect=empty_fn)
    @mock.patch('clickable.device.Device.run_command', side_effect=empty_fn)
    @mock.patch('clickable.commands.install.run_subprocess_check_call', side_effect=empty_fn)
    def test_install_serial_number(self, mock_run_subprocess_check_call, mock_run_command, mock_check_any_attached):
        self.config.device_serial_number = 'foo'
        self.command.run()

        mock_check_any_attached.assert_called_once_with()
        mock_run_subprocess_check_call.assert_called_once_with('adb -s foo push /tmp/build/foo.bar_1.2.3_armhf.click /home/phablet/', cwd='/tmp/build', shell=True)
        mock_run_command.assert_called_once_with(ANY, cwd='/tmp/build')

    @mock.patch('clickable.device.Device.run_command', side_effect=empty_fn)
    @mock.patch('clickable.commands.install.run_subprocess_check_call', side_effect=empty_fn)
    def test_install_scp(self, mock_run_subprocess_check_call, mock_run_command):
        self.config.ssh = 'foo'
        self.command.run()

        mock_run_subprocess_check_call.assert_called_once_with('scp /tmp/build/foo.bar_1.2.3_armhf.click phablet@foo:/home/phablet/', cwd='/tmp/build', shell=True)
        mock_run_command.assert_called_once_with(ANY, cwd='/tmp/build')

    @mock.patch('clickable.device.Device.check_any_attached', side_effect=empty_fn)
    @mock.patch('clickable.device.Device.check_multiple_attached', side_effect=empty_fn)
    @mock.patch('clickable.device.Device.run_command', side_effect=empty_fn)
    @mock.patch('clickable.commands.install.run_subprocess_check_call', side_effect=empty_fn)
    def test_install_adb_with_path(self, mock_run_subprocess_check_call, mock_run_command, mock_check_multiple_attached, mock_check_any_attached):
        self.command.run('/foo/bar.click')

        mock_check_any_attached.assert_called_once_with()
        mock_check_multiple_attached.assert_called_once_with()
        mock_run_subprocess_check_call.assert_called_once_with('adb push /foo/bar.click /home/phablet/', cwd='.', shell=True)
        mock_run_command.assert_called_once_with(ANY, cwd='.')

    @mock.patch('clickable.commands.install.print_warning', side_effect=empty_fn)
    def test_skip_desktop_mode(self, mock_print_warning):
        self.config.desktop = True
        self.command.run()

        mock_print_warning.assert_called_once_with(ANY)

    @mock.patch('clickable.commands.install.print_warning', side_effect=empty_fn)
    def test_skip_container_mode(self, mock_print_warning):
        self.config.container_mode = True
        self.command.run()

        mock_print_warning.assert_called_once_with(ANY)
