from unittest import mock

from clickable.commands.desktop import DesktopCommand
from .base_test import UnitTest


class TestCreateCommand(UnitTest):
    def setUp(self):
        self.setUpConfig()
        self.command = DesktopCommand(self.config)

# TODO test that `CLICKABLE_NVIDIA=1 clickable desktop` yields the same command as `clickable desktop --nvidia`
# TODO implement this
