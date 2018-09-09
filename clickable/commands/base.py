from clickable.container import Container


class Command(object):
    aliases = []
    name = None
    help = ''

    def __init__(self, config):
        self.config = config
        self.container = Container(config)

    def run(self, path_arg=None):
        raise NotImplementedError('run is not yet implemeneted')
