from unittest import mock
from unittest.mock import ANY

from clickable.commands.clean import CleanCommand
from ..mocks import empty_fn, true_fn
from .base_test import UnitTest


def no_file_dir(path):
    if path == '/tmp/build':
        raise OSError('No such file or directory')


def no_file_temp(path):
    if path == '/tmp/build/install':
        raise OSError('No such file or directory')


def dir_exception(path):
    if path == '/tmp/build':
        raise Exception('bad')


def temp_exception(path):
    if path == '/tmp/build/install':
        raise Exception('bad')


class TestCleanCommand(UnitTest):
    def setUp(self):
        self.setUpWithTmpBuildDir()
        self.command = CleanCommand(self.config)

    @mock.patch('shutil.rmtree', side_effect=empty_fn)
    @mock.patch('os.path.exists', side_effect=true_fn)
    @mock.patch('clickable.commands.clean.logger.warning', side_effect=empty_fn)
    def test_clean(self, mock_logger_warning, mock_exists, mock_rmtree):
        self.command.run()

        mock_exists.assert_called_with(ANY)
        mock_rmtree.assert_called_with(ANY)
        mock_logger_warning.assert_not_called()

    @mock.patch('shutil.rmtree', side_effect=no_file_dir)
    @mock.patch('os.path.exists', side_effect=true_fn)
    @mock.patch('clickable.commands.clean.logger.warning', side_effect=empty_fn)
    def test_no_file_dir(self, mock_logger_warning, mock_exists, mock_rmtree):
        self.command.run()

        mock_exists.assert_called_with(ANY)
        mock_rmtree.assert_called_with(ANY)
        mock_logger_warning.assert_not_called()

    @mock.patch('shutil.rmtree', side_effect=no_file_temp)
    @mock.patch('os.path.exists', side_effect=true_fn)
    @mock.patch('clickable.commands.clean.logger.warning', side_effect=empty_fn)
    def test_no_file_temp(self, mock_logger_warning, mock_exists, mock_rmtree):
        self.command.run()

        mock_exists.assert_called_with(ANY)
        mock_rmtree.assert_called_with(ANY)
        mock_logger_warning.assert_not_called()

    @mock.patch('shutil.rmtree', side_effect=dir_exception)
    @mock.patch('os.path.exists', side_effect=true_fn)
    @mock.patch('clickable.commands.clean.logger.warning', side_effect=empty_fn)
    def test_dir_exception(self, mock_logger_warning, mock_exists, mock_rmtree):
        self.command.run()

        mock_exists.assert_called_with(ANY)
        mock_rmtree.assert_called_with(ANY)
        mock_logger_warning.assert_called_with(ANY)

    @mock.patch('shutil.rmtree', side_effect=temp_exception)
    @mock.patch('os.path.exists', side_effect=true_fn)
    @mock.patch('clickable.commands.clean.logger.warning', side_effect=empty_fn)
    def test_temp_exception(self, mock_logger_warning, mock_exists, mock_rmtree):
        self.command.run()

        mock_exists.assert_called_with(ANY)
        mock_rmtree.assert_called_with(ANY)
