from unittest import TestCase, mock

from clickable.commands.create import CreateCommand
from ..mocks import ConfigMock


class TestCreateCommand(TestCase):
    def setUp(self):
        self.config = ConfigMock({})
        self.command = CreateCommand(self.config)


# TODO implement this
