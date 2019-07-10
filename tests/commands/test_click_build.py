from unittest import TestCase, mock
from unittest.mock import ANY

from clickable.commands.click_build import ClickBuildCommand
from clickable.container import Container
from ..mocks import ConfigMock, empty_fn, false_fn


class TestClickBuildCommand(TestCase):
    def setUp(self):
        self.config = ConfigMock()
        self.config.container = Container(self.config)
        self.command = ClickBuildCommand(self.config)

    @mock.patch('clickable.container.Container.run_command', side_effect=empty_fn)
    def test_run(self, mock_run_command):
        self.command.run()

        mock_run_command.assert_called_once_with('click build /fake --no-validate')

    @mock.patch('clickable.container.Container.run_command', side_effect=empty_fn)
    @mock.patch('os.path.exists', side_effect=false_fn)
    @mock.patch('os.makedirs', side_effect=empty_fn)
    @mock.patch('shutil.copyfile', side_effect=empty_fn)
    def test_run_click_output(self, mock_copyfile, mock_makedirs, mock_exists, mock_run_command):
        self.config.click_output = '/foo/bar'
        self.command.run()

        mock_run_command.assert_called_once_with('click build /fake --no-validate')
        mock_exists.assert_called_with(ANY)
        mock_makedirs.assert_called_with(ANY)
        mock_copyfile.assert_called_with(ANY, ANY)
