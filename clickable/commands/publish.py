import os

requests_available = True
try:
    import requests
except ImportError:
    requests_available = False

from .base import Command
from clickable.utils import (
    print_info,
    print_warning,
    print_error,
    print_success,
)


OPENSTORE_API = 'https://open-store.io'
OPENSTORE_API_PATH = '/api/v3/manage/{}/revision'


class PublishCommand(Command):
    aliases = []
    name = 'publish'
    help = 'Publish your click app to the OpenStore'

    def run(self, path_arg=''):
        if not requests_available:
            raise Exception('Unable to publish app, python requests module is not installed')

        if not self.config.apikey:
            print_error('No api key specified, use OPENSTORE_API_KEY or --apikey')
            return

        click = '{}_{}_{}.click'.format(self.config.find_package_name(), self.config.find_version(), self.config.arch)
        click_path = os.path.join(self.config.dir, click)

        url = OPENSTORE_API
        if 'OPENSTORE_API' in os.environ and os.environ['OPENSTORE_API']:
            url = os.environ['OPENSTORE_API']

        url = url + OPENSTORE_API_PATH.format(self.config.find_package_name())
        channel = 'xenial' if self.config.is_xenial else 'vivid'
        files = {'file': open(click_path, 'rb')}
        data = {'channel': channel}
        params = {'apikey': self.config.apikey}

        print_info('Uploading version {} of {} for {} to the OpenStore'.format(self.config.find_version(), self.config.find_package_name(), channel))
        response = requests.post(url, files=files, data=data, params=params)
        if response.status_code == requests.codes.ok:
            print_success('Upload successful')
        else:
            if response.text == 'Unauthorized':
                print_error('Failed to upload click: Unauthorized')
            else:
                print_error('Failed to upload click: {}'.format(response.json()['message']))
