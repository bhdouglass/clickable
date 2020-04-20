from unittest import mock
from unittest.mock import ANY

from clickable.commands.build import BuildCommand
from ..mocks import empty_fn, false_fn
from .base_test import UnitTest


class TestBuildCommand(UnitTest):
    def setUp(self):
        super().setUp()
        self.setUpConfig()
        self.command = BuildCommand(self.config)
        self.click_cmd = 'click build {} --no-validate'.format(self.config.install_dir)

    @mock.patch('clickable.container.Container.run_command', side_effect=empty_fn)
    def test_click_build(self, mock_run_command):
        self.command.click_build()

        mock_run_command.assert_called_once_with(self.click_cmd)

    @mock.patch('clickable.container.Container.run_command', side_effect=empty_fn)
    @mock.patch('os.path.exists', side_effect=false_fn)
    @mock.patch('os.makedirs', side_effect=empty_fn)
    @mock.patch('shutil.copyfile', side_effect=empty_fn)
    def test_click_build_click_output(self, mock_copyfile, mock_makedirs, mock_exists, mock_run_command):
        self.config.click_output = '/foo/bar'
        self.command.click_build()

        mock_run_command.assert_called_once_with(self.click_cmd)
        mock_exists.assert_called_with(ANY)
        mock_makedirs.assert_called_with(ANY)
        mock_copyfile.assert_called_with(ANY, ANY)


# TODO implement more
