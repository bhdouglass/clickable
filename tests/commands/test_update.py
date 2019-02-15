from unittest import TestCase, mock

from clickable.commands.update import UpdateCommand
from ..mocks import ConfigMock, empty_fn


class TestUpdateCommand(TestCase):
    def setUp(self):
        self.config = ConfigMock()
        self.command = UpdateCommand(self.config)

    @mock.patch('clickable.container.Container.check_docker', side_effect=empty_fn)
    @mock.patch('clickable.commands.update.run_subprocess_check_call', side_effect=empty_fn)
    def test_update(self, mock_run_subprocess_check_call, mock_check_docker):
        self.command.run()

        mock_check_docker.assert_called_once()
        mock_run_subprocess_check_call.assert_called()
