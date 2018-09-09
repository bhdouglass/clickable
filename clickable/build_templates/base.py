from clickable.utils import check_command


class Builder(object):
    name = None

    def __init__(self, config, container):
        self.config = config
        self.container = container

        # TODO move
        if not self.config.container_mode:
            if self.config.ssh:
                check_command('ssh')
                check_command('scp')
            else:
                check_command('adb')

    def build(self):
        raise NotImplementedError()
