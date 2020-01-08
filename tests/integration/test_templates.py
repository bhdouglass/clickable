from unittest import TestCase
import os
import shutil

from clickable import Clickable
from clickable.commands.create import CreateCommand
from clickable.container import Container
from ..mocks import ConfigMock


class TestTemplates(TestCase):
    def setUp(self):
        self.clickable = Clickable()
        self.original_path = os.getcwd()

        self.path = os.path.join(os.path.dirname(__file__), 'tmp')
        self.app_path = os.path.join(self.path, 'appname')

        if os.path.exists(self.path):
            shutil.rmtree(self.path)

        os.makedirs(self.path)
        os.chdir(self.path)

        os.environ['CLICKABLE_DEFAULT'] = 'clean build review'

        self.config_file = os.path.expanduser('~/.clickable/cookiecutter_config.yaml')
        self.tmp_config_file = '/tmp/cookiecutter_config.yaml'
        self.restore_config = False
        if os.path.exists(self.config_file):
            shutil.move(self.config_file, self.tmp_config_file)
            self.restore_config = True

    def tearDown(self):
        shutil.rmtree(self.path)
        os.chdir(self.original_path)

        os.environ['CLICKABLE_DEFAULT'] = ''
        os.environ['CLICKABLE_ARCH'] = ''

        if self.restore_config:
            shutil.move(self.tmp_config_file, self.config_file)

    def create_and_run(self, template, arch):
        os.environ['CLICKABLE_ARCH'] = arch

        config = ConfigMock()
        config.container = Container(config)
        command = CreateCommand(config)

        command.run(path_arg=template, no_input=True)

        os.chdir(self.app_path)
        self.clickable.run(['clean', 'build'])

    def assertClickExists(self, arch):
        click = os.path.join(self.app_path, 'build/x86_64-linux-gnu/app/appname.yourname_1.0.0_amd64.click')
        if arch == 'all':
            click = os.path.join(self.app_path, 'build/all/app/appname.yourname_1.0.0_all.click')

        self.assertTrue(os.path.exists(click))

    def test_qml_only(self):
        self.create_and_run('QML Only', 'all')
        self.assertClickExists('all')

    def test_cpp_plugin(self):
        self.create_and_run('C++ (Plugin)', 'amd64')
        self.assertClickExists('amd64')

    def test_cpp_binary(self):
        self.create_and_run('C++ (Binary)', 'amd64')
        self.assertClickExists('amd64')

    def test_python(self):
        self.create_and_run('Python', 'all')
        self.assertClickExists('all')

    def test_html(self):
        self.create_and_run('HTML', 'all')
        self.assertClickExists('all')

    # TODO enable this once the go qt library is fixed
    '''
    def test_go(self):
        self.create_and_run('Go', 'amd64')
        self.assertClickExists('amd64')
    '''

    def test_rust(self):
        self.create_and_run('Rust', 'amd64')
        self.assertClickExists('amd64')
