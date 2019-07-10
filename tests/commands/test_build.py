from unittest import TestCase, mock

from clickable.commands.build import BuildCommand
from clickable.container import Container
from ..mocks import ConfigMock


class TestBuildCommand(TestCase):
    def setUp(self):
        self.config = ConfigMock()
        self.config.container = Container(self.config)
        self.command = BuildCommand(self.config)


# TODO implement this
