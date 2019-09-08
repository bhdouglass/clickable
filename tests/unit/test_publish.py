from unittest import TestCase, mock

from clickable.commands.publish import PublishCommand
from clickable.container import Container
from ..mocks import ConfigMock


class TestPublishCommand(TestCase):
    def setUp(self):
        self.config = ConfigMock()
        self.config.container = Container(self.config)
        self.command = PublishCommand(self.config)


# TODO implement this
