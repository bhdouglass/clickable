from unittest import TestCase, mock

from clickable.build_templates.qmake import QMakeBuilder
from clickable.container import Container
from clickable.device import Device
from ..mocks import ConfigMock


class TestQMakeBuilder(TestCase):
    def setUp(self):
        self.config = ConfigMock({})
        self.container = Container(self.config)
        self.device = Device(self.config)
        self.command = QMakeBuilder(self.config, self.container, self.command)


# TODO implement this
