from unittest import mock
from unittest.mock import ANY

from clickable.commands.create import CreateCommand
from .base_test import UnitTest
from ..mocks import empty_fn


class TestCreateCommand(UnitTest):
    def setUp(self):
        self.setUpConfig()

    @mock.patch('cookiecutter.main.cookiecutter', side_effect=empty_fn)
    def test_create(self, mock_cookiecutter):
        command = CreateCommand(self.config)
        command.run()
        mock_cookiecutter.assert_called_with(ANY, config_file=ANY,
                extra_context={'Copyright Year': ANY}, no_input=False)

# TODO add more
