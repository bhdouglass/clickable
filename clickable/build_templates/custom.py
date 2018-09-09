from .base import Builder
from clickable.config import Config


class CustomBuilder(Builder):
    name = Config.CUSTOM

    def build(self):
        self.container.run_command(self.config.build)
