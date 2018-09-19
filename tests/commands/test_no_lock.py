from unittest import TestCase, mock

from clickable.commands.no_lock import NoLockCommand
from ..mocks import ConfigMock, empty_fn


class TestNoLockCommand(TestCase):
    def setUp(self):
        self.config = ConfigMock({})
        self.command = NoLockCommand(self.config)

    @mock.patch('clickable.device.Device.run_command', side_effect=empty_fn)
    def test_no_lock(self, mock_run_command):
        self.command.run()

        mock_run_command.assert_called_once()
