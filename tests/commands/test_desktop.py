from unittest import TestCase, mock

from clickable.commands.desktop import DesktopCommand
from clickable.container import Container
from ..mocks import ConfigMock


class TestDesktopCommand(TestCase):
    def setUp(self):
        self.config = ConfigMock()
        self.config.container = Container(self.config)
        self.command = DesktopCommand(self.config)


# TODO implement this
