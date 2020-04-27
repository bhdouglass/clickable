class Builder(object):
    name = None

    def __init__(self, config, device):
        self.config = config
        self.device = device

    def build(self):
        raise NotImplementedError()
