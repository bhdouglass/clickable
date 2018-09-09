from clickable.container import Container
from clickable.device import Device


class Command(object):
    aliases = []
    name = None
    help = ''
    skip_auto_detect = False

    def __init__(self, config):
        self.config = config
        self.container = Container(config)
        self.device = Device(config)

    def run(self, path_arg=None):
        raise NotImplementedError('run is not yet implemeneted')
