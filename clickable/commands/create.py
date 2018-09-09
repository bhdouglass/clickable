cookiecutter_available = True
try:
    from cookiecutter.main import cookiecutter
except ImportError:
    cookiecutter_available = False


from .base import Command
from clickable.utils import print_info


APP_TEMPLATES = [
    {
        'name': 'pure-qml-cmake',
        'display': 'Pure QML App (built using CMake)',
        'url': 'https://github.com/bhdouglass/ut-app-pure-qml-cmake-template',
    }, {
        'name': 'cmake',
        'display': 'C++/QML App (built using CMake)',
        'url': 'https://github.com/bhdouglass/ut-app-cmake-template',
    }, {
        'name': 'python-cmake',
        'display': 'Python/QML App (built using CMake)',
        'url': 'https://github.com/bhdouglass/ut-app-python-cmake-template',
    }, {
        'name': 'html',
        'display': 'HTML App',
        'url': 'https://github.com/bhdouglass/ut-app-html-template',
    }, {
        'name': 'webapp',
        'display': 'Simple Webapp',
        'url': 'https://github.com/bhdouglass/ut-app-webapp-template',
    }, {
        'name': 'go',
        'display': 'Go/QML App',
        'url': 'https://github.com/bhdouglass/ut-app-go-template',
    }
]


class CreateCommand(Command):
    aliases = ['init']
    name = 'create'
    help = 'Generate a new app from a list of app template options'
    skip_auto_detect = True

    def run(self, path_arg=None):
        if not cookiecutter_available:
            raise Exception('Cookiecutter is not available on your computer, more information can be found here: https://cookiecutter.readthedocs.io/en/latest/installation.html#install-cookiecutter')

        app_template = None
        if path_arg:
            for template in APP_TEMPLATES:
                if template['name'] == path_arg:
                    app_template = template

        if not app_template:
            print_info('Available app templates:')
            for (index, template) in enumerate(APP_TEMPLATES):
                print('[{}] {} - {}'.format(index + 1, template['name'], template['display']))

            choice = input('Choose an app template [1]: ').strip()
            if not choice:
                choice = '1'

            try:
                choice = int(choice)
            except ValueError:
                raise Exception('Invalid choice')

            if choice > len(APP_TEMPLATES) or choice < 1:
                raise Exception('Invalid choice')

            app_template = APP_TEMPLATES[choice - 1]

        print_info('Generating new app from template: {}'.format(app_template['display']))
        cookiecutter(app_template['url'])

        print_info('Your new app has been generated, go to the app\'s directory and run clickable to get started')
