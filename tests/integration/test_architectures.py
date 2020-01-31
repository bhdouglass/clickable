from unittest import TestCase
import os
import shutil
import argparse

from clickable import Clickable
from clickable.commands.create import CreateCommand
from clickable.container import Container
from clickable.config import Config
from ..mocks import ConfigMock


class TestArchitectures(TestCase):
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

    def create_and_run(self, template, arch, cmd=['clean', 'build'], restrict_arch_env=None, restrict_arch=None, expect_exception=False):
        if restrict_arch_env:
            os.environ['CLICKABLE_ARCH'] = restrict_arch_env

        config = ConfigMock()
        if restrict_arch:
            config.restrict_arch = restrict_arch
        config.container = Container(config)
        command = CreateCommand(config)

        command.run(path_arg=template, no_input=True)

        os.chdir(self.app_path)
        parser = Clickable.create_parser("Integration Test Call")
        run_args = parser.parse_args(['--arch', arch])
        try:
            self.clickable.run(cmd, run_args)
            self.assertFalse(expect_exception)
        except:
            self.assertTrue(expect_exception)

    def assertClickExists(self, arch):
        click = os.path.join(self.app_path, 'build/{}/app/appname.yourname_1.0.0_{}.click'.format(
            Config.arch_triplet_mapping[arch], arch))

        self.assertTrue(os.path.exists(click))

    def test_fail_in_foreign_arch_env(self):
        self.create_and_run('C++ (Binary)', 'amd64', expect_exception=True, restrict_arch_env='armhf')

    def test_arch_all_in_arch_restricted_env(self):
        self.create_and_run('QML Only', 'all', restrict_arch_env='armhf')
        self.assertClickExists('all')

    def test_none_build_cmd_in_foreign_arch_env(self):
        self.create_and_run('C++ (Binary)', 'amd64', cmd = ['clean'], restrict_arch_env='armhf')

    def test_fail_in_restricted_arch(self):
        self.create_and_run('C++ (Binary)', 'amd64', expect_exception=True, restrict_arch='armhf')
        self.create_and_run('QML Only', 'all', expect_exception=True, restrict_arch='armhf')

    def test_fail_none_build_cmd_in_restricted_arch(self):
        self.create_and_run('C++ (Binary)', 'amd64', cmd = ['clean'], expect_exception=True, restrict_arch='armhf')
