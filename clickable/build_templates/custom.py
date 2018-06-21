from .base import Clickable


class CustomClickable(Clickable):
    def _build(self):
        self.run_container_command(self.config.build)
