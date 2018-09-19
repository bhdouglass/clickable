from unittest import TestCase, mock

from clickable.commands.build import BuildCommand
from ..mocks import ConfigMock


class TestBuildCommand(TestCase):
    def setUp(self):
        self.config = ConfigMock({})
        self.command = BuildCommand(self.config)


# TODO implement this
