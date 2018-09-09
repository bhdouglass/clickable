from .base import Command
from clickable.utils import print_warning


class LaunchCommand(Command):
    aliases = []
    name = 'launch'
    help = 'Launches the app on a device'

    def kill(self):
        if self.config.desktop:
            print_warning('Skipping kill, running in desktop mode')
            return
        elif self.config.container_mode:
            print_warning('Skipping kill, running in container mode')
            return

        if self.config.kill:
            try:
                self.device.run_command('pkill {}'.format(self.config.kill))
            except Exception:
                pass  # Nothing to do, the process probably wasn't running

    def run(self, path_arg=None):
        cwd = '.'
        if path_arg:
            app = path_arg
        else:
            self.kill()

            app = '{}_{}_{}'.format(self.config.find_package_name(), self.config.find_app_name(), self.config.find_version())
            cwd = self.config.dir

        launch = 'ubuntu-app-launch {}'.format(app)
        if self.config.launch:
            launch = self.config.launch

        self.device.run_command('sleep 1s && {}'.format(launch), cwd=cwd)
