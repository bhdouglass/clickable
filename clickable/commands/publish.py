import os
import urllib.parse

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
            raise Exception('No api key specified, use OPENSTORE_API_KEY or --apikey')

        click = self.config.get_click_filename()
        click_path = os.path.join(self.config.build_dir, click)

        url = OPENSTORE_API
        if 'OPENSTORE_API' in os.environ and os.environ['OPENSTORE_API']:
            url = os.environ['OPENSTORE_API']

        package_name = self.config.find_package_name()
        url = url + OPENSTORE_API_PATH.format(package_name)
        channel = 'xenial' if self.config.is_xenial else 'vivid'
        files = {'file': open(click_path, 'rb')}
        data = {
            'channel': channel,
            'changelog': path_arg,
        }
        params = {'apikey': self.config.apikey}

        print_info('Uploading version {} of {} for {} to the OpenStore'.format(self.config.find_version(), package_name, channel))
        response = requests.post(url, files=files, data=data, params=params)
        if response.status_code == requests.codes.ok:
            print_success('Upload successful')
        elif response.status_code == requests.codes.not_found:
            title = urllib.parse.quote(self.config.find_package_title())
            raise Exception(
                'App needs to be created in the OpenStore before you can publish it. Visit {}/submit?appId={}&name={}'.format(
                    OPENSTORE_API,
                    package_name,
                    title,
                )
            )
        else:
            if response.text == 'Unauthorized':
                raise Exception('Failed to upload click: Unauthorized')
            else:
                raise Exception('Failed to upload click: {}'.format(response.json()['message']))
