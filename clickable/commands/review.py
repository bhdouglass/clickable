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
            click = '{}_{}_{}.click'.format(self.config.find_package_name(), self.config.find_version(), self.config.arch)
            click_path = os.path.join(self.config.dir, click)

        cwd = os.path.dirname(os.path.realpath(click_path))
        self.container.run_command('click-review {}'.format(click_path), use_dir=False, cwd=cwd)
