from unittest import TestCase, mock

from clickable.commands.writable_image import WritableImageCommand
from ..mocks import ConfigMock, empty_fn


class TestWritableImageCommand(TestCase):
    def setUp(self):
        self.config = ConfigMock({})
        self.command = WritableImageCommand(self.config)

    @mock.patch('clickable.device.Device.run_command', side_effect=empty_fn)
    def test_writable_image(self, mock_run_command):
        self.command.run()

        mock_run_command.assert_called_once()
