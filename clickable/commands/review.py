import os
import subprocess

from .base import Command


class ReviewCommand(Command):
    aliases = []
    name = 'review'
    help = 'Takes the built click package and runs click-review against it'

    def check(self, path=None, raise_on_error=False, raise_on_warning=False):
        if path:
            click = os.path.basename(path)
            click_path = path
        else:
            click = self.config.install_files.get_click_filename()
            click_path = os.path.join(self.config.build_dir, click)

        cwd = os.path.dirname(os.path.realpath(click_path))

        try:
            self.config.container.run_command('click-review {}'.format(click_path), use_build_dir=False, cwd=cwd)
        except subprocess.CalledProcessError as e:
            if e.returncode == 2 and not raise_on_error:
                pass
            elif e.returncode == 3 and not raise_on_warning:
                pass
            else:
                raise e

    def run(self, path_arg=None):
        self.check(path_arg)
