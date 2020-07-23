import os
from datetime import datetime

from .base import Command
from clickable.exceptions import ClickableException

cookiecutter_available = True
try:
    import cookiecutter.main
except ImportError:
    cookiecutter_available = False


COOKIECUTTER_URL = 'https://gitlab.com/clickable/ut-app-meta-template.git'


# Map old template names to new template names
TEMPLATE_MAP = {
    'pure-qml-cmake': 'QML Only',
    'cmake': 'C++ (Plugin)',
    'python-cmake': 'Python',
    'html': 'HTML',
    'go': 'Go',
    'main-cpp': 'C++ (Binary)',
    'rust': 'Rust',
}


class CreateCommand(Command):
    aliases = ['init']
    name = 'create'
    help = 'Generate a new app from a list of app template options'

    def run(self, path_arg=None):
        if not cookiecutter_available:
            raise ClickableException('Cookiecutter is not available on your computer, more information can be found here: https://cookiecutter.readthedocs.io/en/latest/installation.html#install-cookiecutter')

        config_file = os.path.expanduser('~/.clickable/cookiecutter_config.yaml')
        if not os.path.isfile(config_file):
            config_file = None

        extra_context = {
            'Copyright Year': datetime.now().year
        }
        if path_arg:
            if path_arg in TEMPLATE_MAP:
                extra_context['Template'] = TEMPLATE_MAP[path_arg]
            else:
                extra_context['Template'] = path_arg

        no_input = not self.config.interactive

        try:
            cookiecutter.main.cookiecutter(
                COOKIECUTTER_URL,
                extra_context=extra_context,
                no_input=no_input,
                config_file=config_file,
            )
        except cookiecutter.exceptions.FailedHookException as err:
            raise ClickableException('Failed to create app, see logs above')
