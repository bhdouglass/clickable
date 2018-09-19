from unittest import TestCase, mock

from clickable.build_templates.cordova import CordovaBuilder
from clickable.container import Container
from clickable.device import Device
from ..mocks import ConfigMock


class TestCordovaBuilder(TestCase):
    def setUp(self):
        self.config = ConfigMock({})
        self.container = Container(self.config)
        self.device = Device(self.config)
        self.command = CordovaBuilder(self.config, self.container, self.command)


# TODO implement this
