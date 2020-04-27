import os
import urllib.parse

requests_available = True
try:
    import requests
except ImportError:
    requests_available = False

from .base import Command
from clickable.logger import logger
from clickable.exceptions import ClickableException


OPENSTORE_API = 'https://open-store.io'
OPENSTORE_API_PATH = '/api/v3/manage/{}/revision'


class PublishCommand(Command):
    aliases = []
    name = 'publish'
    help = 'Publish your click app to the OpenStore'

    def run(self, path_arg=''):
        if not requests_available:
            raise ClickableException('Unable to publish app, python requests module is not installed')

        if not self.config.apikey:
            raise ClickableException('No api key specified, use OPENSTORE_API_KEY or --apikey')

        click = self.config.install_files.get_click_filename()
        click_path = os.path.join(self.config.build_dir, click)

        url = OPENSTORE_API
        if 'OPENSTORE_API' in os.environ and os.environ['OPENSTORE_API']:
            url = os.environ['OPENSTORE_API']

        package_name = self.config.install_files.find_package_name()
        url = url + OPENSTORE_API_PATH.format(package_name)
        channel = 'xenial'
        files = {'file': open(click_path, 'rb')}
        data = {
            'channel': channel,
            'changelog': path_arg.encode('utf8', 'surrogateescape'),
        }
        params = {'apikey': self.config.apikey}

        logger.info('Uploading version {} of {} for {}/{} to the OpenStore'.format(
            self.config.install_files.find_version(),
            package_name,
            channel,
            self.config.arch,
        ))
        response = requests.post(url, files=files, data=data, params=params)
        if response.status_code == requests.codes.ok:
            logger.info('Upload successful')
        elif response.status_code == requests.codes.not_found:
            title = urllib.parse.quote(self.config.install_files.find_package_title())
            raise ClickableException(
                'App needs to be created in the OpenStore before you can publish it. Visit {}/submit?appId={}&name={}'.format(
                    OPENSTORE_API,
                    package_name,
                    title,
                )
            )
        else:
            if response.text == 'Unauthorized':
                raise ClickableException('Failed to upload click: Unauthorized')
            else:
                raise ClickableException('Failed to upload click: {}'.format(response.json()['message']))
