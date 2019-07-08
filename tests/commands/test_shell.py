from unittest import TestCase, mock

from clickable.commands.shell import ShellCommand
from clickable.container import Container
from ..mocks import ConfigMock


class TestShellCommand(TestCase):
    def setUp(self):
        self.config = ConfigMock()
        self.config.container = Container(self.config)
        self.command = ShellCommand(self.config)


# TODO implement this
