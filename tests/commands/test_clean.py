from unittest import TestCase, mock

from clickable.commands.clean import CleanCommand
from ..mocks import ConfigMock, empty_fn, true_fn


def no_file_dir(path):
    if path == '/tmp/build':
        raise OSError('No such file or directory')


def no_file_temp(path):
    if path == '/tmp/build/tmp':
        raise OSError('No such file or directory')


def dir_exception(path):
    if path == '/tmp/build':
        raise Exception('bad')


def temp_exception(path):
    if path == '/tmp/build/tmp':
        raise Exception('bad')


class TestCleanCommand(TestCase):
    def setUp(self):
        self.config = ConfigMock({})
        self.command = CleanCommand(self.config)

    @mock.patch('shutil.rmtree', side_effect=empty_fn)
    @mock.patch('os.path.exists', side_effect=true_fn)
    @mock.patch('clickable.commands.clean.print_warning', side_effect=empty_fn)
    def test_clean(self, mock_print_warning, mock_exists, mock_rmtree):
        self.command.run()

        mock_exists.assert_called()
        mock_rmtree.assert_called()
        mock_print_warning.assert_not_called()

    @mock.patch('shutil.rmtree', side_effect=no_file_dir)
    @mock.patch('os.path.exists', side_effect=true_fn)
    @mock.patch('clickable.commands.clean.print_warning', side_effect=empty_fn)
    def test_no_file_dir(self, mock_print_warning, mock_exists, mock_rmtree):
        self.command.run()

        mock_exists.assert_called()
        mock_rmtree.assert_called()
        mock_print_warning.assert_not_called()

    @mock.patch('shutil.rmtree', side_effect=no_file_temp)
    @mock.patch('os.path.exists', side_effect=true_fn)
    @mock.patch('clickable.commands.clean.print_warning', side_effect=empty_fn)
    def test_no_file_temp(self, mock_print_warning, mock_exists, mock_rmtree):
        self.command.run()

        mock_exists.assert_called()
        mock_rmtree.assert_called()
        mock_print_warning.assert_not_called()

    @mock.patch('shutil.rmtree', side_effect=dir_exception)
    @mock.patch('os.path.exists', side_effect=true_fn)
    @mock.patch('clickable.commands.clean.print_warning', side_effect=empty_fn)
    def test_dir_exception(self, mock_print_warning, mock_exists, mock_rmtree):
        self.command.run()

        mock_exists.assert_called()
        mock_rmtree.assert_called()
        mock_print_warning.assert_called()

    @mock.patch('shutil.rmtree', side_effect=temp_exception)
    @mock.patch('os.path.exists', side_effect=true_fn)
    @mock.patch('clickable.commands.clean.print_warning', side_effect=empty_fn)
    def test_temp_exception(self, mock_print_warning, mock_exists, mock_rmtree):
        self.command.run()

        mock_exists.assert_called()
        mock_rmtree.assert_called()
        mock_print_warning.assert_called()
