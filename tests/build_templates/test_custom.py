from unittest import TestCase, mock

from clickable.build_templates.custom import CustomBuilder
from clickable.container import Container
from clickable.device import Device
from ..mocks import ConfigMock


class TestCustomBuilder(TestCase):
    def setUp(self):
        self.config = ConfigMock({})
        self.container = Container(self.config)
        self.device = Device(self.config)
        self.command = CustomBuilder(self.config, self.container, self.command)


# TODO implement this
