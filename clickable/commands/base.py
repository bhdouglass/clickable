from clickable.device import Device


class Command(object):
    aliases = []
    name = None
    help = ''

    def __init__(self, config):
        self.config = config
        self.device = Device(config)

    def run(self, path_arg=None):
        raise NotImplementedError('run is not yet implemeneted')

    def preprocess(self, path_arg=None):
        pass  # Implemented in subclasses
