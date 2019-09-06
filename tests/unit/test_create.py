from unittest import TestCase, mock

from clickable.commands.create import CreateCommand
from clickable.container import Container
from ..mocks import ConfigMock


class TestCreateCommand(TestCase):
    def setUp(self):
        self.config = ConfigMock()
        self.config.container = Container(self.config)
        self.command = CreateCommand(self.config)


# TODO implement this
