from unittest import TestCase, mock

from clickable.build_templates.pure import PureQMLMakeBuilder
from clickable.container import Container
from clickable.device import Device
from ..mocks import ConfigMock


class TestPureQMLMakeBuilder(TestCase):
    def setUp(self):
        self.config = ConfigMock({})
        self.container = Container(self.config)
        self.device = Device(self.config)
        self.command = PureQMLMakeBuilder(self.config, self.command)


# TODO implement this
