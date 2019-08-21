from unittest import TestCase, mock

from clickable.commands.desktop import DesktopCommand
from clickable.container import Container
from ..mocks import ConfigMock


class TestDesktopCommand(TestCase):
    def setUp(self):
        self.config = ConfigMock()
        self.config.container = Container(self.config)
        self.command = DesktopCommand(self.config)

# TODO test that `CLICKABLE_NVIDIA=1 clickable desktop` yields the same command as `clickable desktop --nvidia`
# TODO implement this
