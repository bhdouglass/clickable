from unittest import TestCase, mock

from clickable.commands.review import ReviewCommand
from clickable.container import Container
from ..mocks import ConfigMock, empty_fn


class TestReviewCommand(TestCase):
    def setUp(self):
        self.config = ConfigMock()
        self.config.container = Container(self.config)
        self.command = ReviewCommand(self.config)

    @mock.patch('clickable.container.Container.run_command', side_effect=empty_fn)
    def test_run(self, mock_run_command):
        self.command.run()

        mock_run_command.assert_called_once_with('click-review /tmp/build/foo.bar_1.2.3_armhf.click', cwd='/tmp/build', use_dir=False)

    @mock.patch('clickable.container.Container.run_command', side_effect=empty_fn)
    def test_run_with_path_arg(self, mock_run_command):
        self.command.run('/foo/bar.click')

        mock_run_command.assert_called_once_with('click-review /foo/bar.click', cwd='/foo', use_dir=False)
