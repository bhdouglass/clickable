import os

from .base import Command


class ReviewCommand(Command):
    aliases = []
    name = 'review'
    help = 'Takes the built click package and runs click-review against it'

    def run(self, path_arg=None):
        if path_arg:
            click = os.path.basename(path_arg)
            click_path = path_arg
        else:
            click = self.config.install_files.get_click_filename()
            click_path = os.path.join(self.config.build_dir, click)

        cwd = os.path.dirname(os.path.realpath(click_path))
        self.config.container.run_command('click-review {}'.format(click_path), use_build_dir=False, cwd=cwd)
