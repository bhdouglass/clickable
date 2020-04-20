from unittest import mock
from unittest.mock import ANY

from clickable.commands.no_lock import NoLockCommand
from ..mocks import empty_fn
from .base_test import UnitTest


class TestNoLockCommand(UnitTest):
    def setUp(self):
        self.setUpConfig()
        self.command = NoLockCommand(self.config)

    @mock.patch('clickable.device.Device.run_command', side_effect=empty_fn)
    def test_no_lock(self, mock_run_command):
        self.command.run()

        mock_run_command.assert_called_once_with(ANY, cwd=ANY)
