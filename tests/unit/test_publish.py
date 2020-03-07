from unittest import mock

from clickable.commands.publish import PublishCommand
from .base_test import UnitTest


class TestPublishCommand(UnitTest):
    def setUp(self):
        self.setUpConfig()
        self.command = PublishCommand(self.config)


# TODO implement this
