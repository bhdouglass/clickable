import subprocess
import shlex
import getpass

from .base import Command
from clickable.utils import print_info, run_subprocess_check_output


class SetupDockerCommand(Command):
    aliases = ['setup_docker']
    name = 'setup-docker'
    help = 'Configure docker for use with clickable'

    def run(self, path_arg=None):
        self.container.start_docker()

        group_exists = False
        with open('/etc/group', 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith('docker:'):
                    group_exists = True

        if not group_exists:
            print_info('Asking for root to create docker group')
            subprocess.check_call(shlex.split('sudo groupadd docker'))

        output = run_subprocess_check_output(shlex.split('groups {}'.format(getpass.getuser()))).strip()
        # Test for exactly docker in the group list
        if ' docker ' in output or output.endswith(' docker') or output.startswith('docker ') or output == 'docker':
            print_info('Setup has already been completed')
        else:
            print_info('Asking for root to add the current user to the docker group')
            subprocess.check_call(shlex.split('sudo usermod -aG docker {}'.format(getpass.getuser())))

            print_info('Log out or restart to apply changes')
