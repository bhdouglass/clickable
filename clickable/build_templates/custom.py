from .base import Builder
from clickable.config.config import Config
from clickable.config.constants import Constants


class CustomBuilder(Builder):
    name = Constants.CUSTOM

    def build(self):
        self.config.container.run_command(self.config.build)
