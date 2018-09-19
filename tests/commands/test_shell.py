from unittest import TestCase, mock

from clickable.commands.shell import ShellCommand
from ..mocks import ConfigMock


class TestShellCommand(TestCase):
    def setUp(self):
        self.config = ConfigMock({})
        self.command = ShellCommand(self.config)


# TODO implement this
