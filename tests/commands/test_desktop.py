from unittest import TestCase, mock

from clickable.commands.desktop import DesktopCommand
from ..mocks import ConfigMock


class TestDesktopCommand(TestCase):
    def setUp(self):
        self.config = ConfigMock()
        self.command = DesktopCommand(self.config)


# TODO implement this
