from unittest import TestCase
import os
import shutil

from clickable.container import Container
from clickable.commands.create import CreateCommand
from clickable.exceptions import ClickableException
from ..mocks import ClickableMock, ConfigMock

class IntegrationTest(TestCase):
    def setUpConfig(self,
                    expect_exception=False,
                    mock_config_json={},
                    mock_config_env={},
                    *args, **kwargs):
        IntegrationTest.setUp(self)

        self.config = None
        try:
            self.config = ConfigMock(
                mock_config_json=mock_config_json,
                mock_config_env=mock_config_env,
                mock_install_files=True,
                *args, **kwargs
            )
            self.config.container = Container(self.config)
            self.config.interactive = False
            if expect_exception:
                raise ClickableException("A ClickableException was expected, but was not raised")
        except ClickableException as e:
            if not expect_exception:
                raise e

    def setUp(self):
        self.clickable = None
        self.test_dir = os.path.abspath("tests/tmp")
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def tearDown(self):
        self.clickable = None
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def run_clickable(self,
                 cli_args=[],
                 expect_exception=False,
                 config_json=None,
                 config_env=None):
        """
        Generic test run function

        :param list cli_args: command line to call clickable with
        :param bool expect_exception: asserts an ClickableException to be raised
                    (True) or not to be raised (False)
        :param dict config_json: config to be used instead of loading the
                    clickable.json
        :param dict config_env: env vars to be used instead of using system
                    env vars
        """
        self.clickable = ClickableMock(mock_config_json=config_json,
                                       mock_config_env=config_env)

        try:
            self.clickable.run_clickable(cli_args)
            if expect_exception:
                raise ClickableException("A ClickableException was expected, but was not raised")
        except ClickableException as e:
            if not expect_exception:
                raise e
