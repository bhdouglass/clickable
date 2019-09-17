from clickable.libconfig import LibConfig
from unittest.mock import Mock


class LibConfigMock(LibConfig):
    def __init__(self, json_config):
        super().__init__(name='testlib', json_config=json_config,
                         arch='amd64', root_dir='/tmp', debug_build=False)
        self.cwd = '/tmp'
        self.config['build_dir'] = '/tmp/build'
        self.config['install_dir'] = '/tmp/build/tmp'

