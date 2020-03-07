from unittest import mock

from clickable.commands.shell import ShellCommand
from .base_test import UnitTest


class TestShellCommand(UnitTest):
    def setUp(self):
        self.setUpConfig()
        self.command = ShellCommand(self.config)


# TODO implement this
