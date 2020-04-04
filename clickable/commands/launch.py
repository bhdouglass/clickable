from .base import Command
from clickable.logger import logger


class LaunchCommand(Command):
    aliases = []
    name = 'launch'
    help = 'Launches the app on a device'

    def kill(self):
        if self.config.is_desktop_mode():
            logger.debug('Skipping kill, running in desktop mode')
            return
        elif self.config.container_mode:
            logger.debug('Skipping kill, running in container mode')
            return

        if self.config.kill:
            try:
                # Enclose first character in square brackets to prevent
                # spurious error when running `pkill -f` over `adb`
                kill = '[' + self.config.kill[:1] + ']' + self.config.kill[1:]
                self.device.run_command('pkill -f \\"{}\\"'.format(kill))
            except Exception:
                pass  # Nothing to do, the process probably wasn't running

    def preprocess(self, path_arg=None):
        if not path_arg:
            self.kill()

    def run(self, path_arg=None):
        cwd = '.'
        if path_arg:
            app = path_arg
        else:
            app = self.config.install_files.find_full_package_name()
            cwd = self.config.build_dir

        launch = 'ubuntu-app-launch {}'.format(app)
        if self.config.launch:
            launch = self.config.launch

        self.device.run_command('sleep 1s && {}'.format(launch), cwd=cwd)
