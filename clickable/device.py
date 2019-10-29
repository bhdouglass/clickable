import subprocess
import shlex

from .utils import run_subprocess_check_output
from .exceptions import ClickableException
from .logger import logger


class Device(object):
    def __init__(self, config):
        self.config = config

    def detect_attached(self):
        output = run_subprocess_check_output(shlex.split('adb devices -l')).strip()
        devices = []
        for line in output.split('\n'):
            if 'device' in line and 'devices' not in line:
                device = line.split(' ')[0]
                for part in line.split(' '):
                    if part.startswith('model:'):
                        device = '{} - {}'.format(device, part.replace('model:', '').replace('_', ' ').strip())

                devices.append(device)

        return devices

    def check_any_attached(self):
        devices = self.detect_attached()
        if len(devices) == 0:
            raise ClickableException('No devices available via adb')

    def check_multiple_attached(self):
        devices = self.detect_attached()
        if len(devices) > 1 and not self.config.device_serial_number:
            raise ClickableException('Multiple devices detected via adb')

    def run_command(self, command, cwd=None):
        if self.config.container_mode:
            logger.debug('Skipping device command, running in container mode')
            return

        if not cwd:
            cwd = self.config.build_dir

        wrapped_command = ''
        if self.config.ssh:
            wrapped_command = 'echo "{}" | ssh phablet@{}'.format(command, self.config.ssh)
        else:
            self.check_any_attached()

            if self.config.device_serial_number:
                wrapped_command = 'adb -s {} shell "{}"'.format(self.config.device_serial_number, command)
            else:
                self.check_multiple_attached()
                wrapped_command = 'adb shell "{}"'.format(command)

        subprocess.check_call(wrapped_command, cwd=cwd, shell=True)
