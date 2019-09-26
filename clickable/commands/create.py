from .base import Command
from clickable.logger import logger
from clickable.exceptions import ClickableException

cookiecutter_available = True
try:
    from cookiecutter.main import cookiecutter
except ImportError:
    cookiecutter_available = False

APP_TEMPLATES = [
    {
        'name': 'pure-qml-cmake',
        'display': 'Pure QML App (built using CMake)',
        'url': 'https://gitlab.com/clickable/ut-app-pure-qml-cmake-template',
    }, {
        'name': 'cmake',
        'display': 'C++/QML App (built using CMake)',
        'url': 'https://gitlab.com/clickable/ut-app-cmake-template',
    }, {
        'name': 'python-cmake',
        'display': 'Python/QML App (built using CMake)',
        'url': 'https://gitlab.com/clickable/ut-app-python-cmake-template',
    }, {
        'name': 'html',
        'display': 'HTML App',
        'url': 'https://gitlab.com/clickable/ut-app-html-template',
    }, {
        'name': 'webapp',
        'display': 'Simple Webapp',
        'url': 'https://gitlab.com/clickable/ut-app-webapp-template',
    }, {
        'name': 'go',
        'display': 'Go/QML App',
        'url': 'https://gitlab.com/clickable/ut-app-go-template',
    }, {
        'name': 'main-cpp',
        'display': 'C++/QML App (built using CMake with a main.cpp)',
        'url': 'https://gitlab.com/clickable/ut-app-binary-cmake-template',
    }, {
        'name': 'rust',
        'display': 'Rust/QML App',
        'url': 'https://gitlab.com/clickable/ut-app-rust-template',
    }
]


class CreateCommand(Command):
    aliases = ['init']
    name = 'create'
    help = 'Generate a new app from a list of app template options'

    def run(self, path_arg=None, no_input=False):
        if not cookiecutter_available:
            raise ClickableException('Cookiecutter is not available on your computer, more information can be found here: https://cookiecutter.readthedocs.io/en/latest/installation.html#install-cookiecutter')

        app_template = None
        if path_arg:
            for template in APP_TEMPLATES:
                if template['name'] == path_arg:
                    app_template = template

        if not app_template:
            logger.info('Available app templates:')
            for (index, template) in enumerate(APP_TEMPLATES):
                print('[{}] {} - {}'.format(index + 1, template['name'], template['display']))

            choice = input('Choose an app template [1]: ').strip()
            if not choice:
                choice = '1'

            try:
                choice = int(choice)
            except ValueError:
                raise ClickableException('Invalid choice')

            if choice > len(APP_TEMPLATES) or choice < 1:
                raise ClickableException('Invalid choice')

            app_template = APP_TEMPLATES[choice - 1]

        logger.info('Generating new app from template: {}'.format(app_template['display']))
        cookiecutter(app_template['url'], no_input=no_input)

        logger.info('Your new app has been generated, go to the app\'s directory and run clickable to get started')
