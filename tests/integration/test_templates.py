from unittest import TestCase, mock
import os
import shutil
import json

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
        os.environ['CLICKABLE_ARCH'] = 'amd64'

    def tearDown(self):
        #shutil.rmtree(self.path)
        os.chdir(self.original_path)

        os.environ['CLICKABLE_DEFAULT'] = ''
        os.environ['CLICKABLE_ARCH'] = ''

    def create_and_run(self, template):
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

    def test_pure_qml_cmake(self):
        self.create_and_run('pure-qml-cmake')
        self.assertClickExists('all')

    def test_cmake(self):
        self.create_and_run('cmake')
        self.assertClickExists('amd64')

    def test_python_cmake(self):
        self.create_and_run('python-cmake')
        self.assertClickExists('all')

    def test_html(self):
        self.create_and_run('html')
        self.assertClickExists('all')

    def test_webapp(self):
        self.create_and_run('webapp')
        self.assertClickExists('all')

    def test_main_cpp(self):
        self.create_and_run('main-cpp')
        self.assertClickExists('amd64')

    # TODO enable this once the go qt library is fixed
    '''
    def test_go(self):
        self.create_and_run('go')
        self.assertClickExists('amd64')
    '''

    def test_rust(self):
        # TOOD see if the rust template can support automatically changing the arch in the manifest

        config = ConfigMock()
        config.container = Container(config)
        command = CreateCommand(config)

        command.run(path_arg='rust', no_input=True)

        manifest_path = os.path.join(self.app_path, 'click/manifest.json')
        with open(manifest_path, 'r') as manifest_reader:
            manifest = json.load(manifest_reader)
            manifest['architecture'] = 'amd64'

            with open(manifest_path, 'w') as manifest_writer:
                json.dump(manifest, manifest_writer, indent=4)

        os.chdir(self.app_path)
        self.clickable.run(['clean', 'build'])

        self.assertClickExists('amd64')
