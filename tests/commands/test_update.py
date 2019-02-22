from unittest import TestCase, mock
from unittest.mock import ANY

from clickable.commands.update import UpdateCommand
from ..mocks import ConfigMock, empty_fn


def string_fn(*args, **kwargs):
    return 'string'


class TestUpdateCommand(TestCase):
    def setUp(self):
        self.config = ConfigMock()
        self.command = UpdateCommand(self.config)

    @mock.patch('clickable.container.Container.check_docker', side_effect=empty_fn)
    @mock.patch('clickable.commands.update.run_subprocess_check_output', side_effect=string_fn)
    @mock.patch('clickable.commands.update.run_subprocess_check_call', side_effect=empty_fn)
    def test_update(self, mock_run_subprocess_check_call, mock_run_subprocess_check_output, mock_check_docker):
        self.command.run()

        mock_check_docker.assert_called_once_with()
        mock_run_subprocess_check_output.assert_called_once_with(ANY)
        mock_run_subprocess_check_call.assert_called_with(ANY)
