from unittest import TestCase, mock

from clickable.commands.publish import PublishCommand
from ..mocks import ConfigMock


class TestPublishCommand(TestCase):
    def setUp(self):
        self.config = ConfigMock({})
        self.command = PublishCommand(self.config)


# TODO implement this
