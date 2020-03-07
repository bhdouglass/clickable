from unittest import mock
from unittest.mock import ANY

from clickable.commands.writable_image import WritableImageCommand
from ..mocks import empty_fn
from .base_test import UnitTest


class TestWritableImageCommand(UnitTest):
    def setUp(self):
        self.setUpConfig()
        self.command = WritableImageCommand(self.config)

    @mock.patch('clickable.device.Device.run_command', side_effect=empty_fn)
    def test_writable_image(self, mock_run_command):
        self.command.run()

        mock_run_command.assert_called_once_with(ANY, cwd=ANY)
