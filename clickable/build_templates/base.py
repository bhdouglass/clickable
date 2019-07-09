class Builder(object):
    name = None

    def __init__(self, config, container, device):
        self.config = config
        self.config.container = container
        self.device = device

    def build(self):
        raise NotImplementedError()
