from clickable.config import Config


class ConfigMock(Config):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cwd = '/tmp'
        self.config['dir'] = '/tmp/build'
        self.temp = '/tmp/build/tmp'

    def load_json_config(self):
        return {}

    def load_env_config(self):
        return {}

    def load_arg_config(self, *args):
        return {}

    def find_manifest(self, *args):
        return '/fake/manifest.json'

    def get_manifest(self):
        return {
            'version': '1.2.3',
            'name': 'foo.bar',
            'hooks': {
                'foo': {
                    'desktop': '/fake/foo.desktop',
                },
            },
        }
