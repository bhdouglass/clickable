from unittest import mock
from unittest.mock import ANY

from clickable.commands.devices import DevicesCommand
from ..mocks import empty_fn
from .base_test import UnitTest


def no_devices(*args, **kwargs):
    return []


def devices(*args, **kwargs):
    return ['foo - bar']


class TestDevicesCommand(UnitTest):
    def setUp(self):
        self.setUpConfig()
        self.command = DevicesCommand(self.config)

    @mock.patch('clickable.device.Device.detect_attached', side_effect=no_devices)
    @mock.patch('clickable.commands.devices.logger.warning', side_effect=empty_fn)
    def test_no_devices(self, mock_logger_warning, mock_detect_attached):
        self.command.run()

        mock_detect_attached.assert_called_once_with()
        mock_logger_warning.assert_called_once_with('No attached devices')

    @mock.patch('clickable.device.Device.detect_attached', side_effect=devices)
    @mock.patch('clickable.commands.devices.logger.info', side_effect=empty_fn)
    def test_no_devices(self, mock_logger_info, mock_detect_attached):
        self.command.run()

        mock_detect_attached.assert_called_once_with()
        mock_logger_info.assert_called_once_with('foo - bar')
