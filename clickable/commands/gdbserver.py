import os
import sys
import signal

from .base import Command
from clickable.utils import (
    run_subprocess_call,
    run_subprocess_check_output,
)
from clickable.logger import logger
from clickable.exceptions import ClickableException

class GdbserverCommand(Command):
    aliases = []
    name = 'gdbserver'
    help = 'Opens a gdbserver session on the device accessible at localhost:3333'

    def set_signal_handler(self):
        def signal_handler(sig, frame):
            self.kill_gdbserver()
            sys.exit(0)
        signal.signal(signal.SIGINT, signal_handler)

    def get_app_dir(self):
        return "/opt/click.ubuntu.com/{}/current".format(
            self.config.install_files.find_package_name(),
        )

    def get_app_id(self):
        return "{}_{}_{}".format(
            self.config.install_files.find_package_name(),
            self.config.install_files.find_app_name(),
            self.config.install_files.find_version(),
        )

    def get_app_exec(self):
        desktop = self.config.install_files.get_desktop(self.config.install_dir)
        return desktop["Exec"]

    def get_app_exec_full_path(self):
        app_dir = self.get_app_dir()
        environ = self.get_app_env()
        app_exec = self.get_app_exec().split()

        commands = ["cd {}".format(app_dir),
                    "PATH={} which {}".format(environ["PATH"], app_exec[0])]
        output = self.device.run_command(commands, get_output=True).strip()
        path = output.splitlines()[-1]

        if app_exec[0] not in path:
            raise ClickableException("Could not find app executable in PATH on the device.")

        app_exec[0] = path
        return " ".join(app_exec)

    def get_app_env(self):
        package_name = self.config.install_files.find_package_name()
        app_name = self.config.install_files.find_app_name()
        app_id = self.get_app_id()

        environ = {
            "APP_DESKTOP_FILE_PATH": "/opt/click.ubuntu.com/.click/users/phablet/{}/{}.desktop".format(package_name, app_name),
            "APP_DIR": "/opt/click.ubuntu.com/.click/users/phablet/{}".format(package_name),
            "APP_EXEC": self.get_app_exec(),
            "APP_ID": app_id,
            "__GL_SHADER_DISK_CACHE_PATH": "/home/phablet/.cache/{}".format(package_name),
            "TMPDIR": "/run/user/32011/confined/{}".format(package_name),
            "UPSTART_INSTANCE": app_id,
            "XDG_DATA_DIRS": "/opt/click.ubuntu.com/.click/users/phablet/{}:/usr/share/ubuntu-touch:/usr/share/ubuntu-touch:/usr/local/share/:/usr/share/:/custom/usr/share/".format(package_name),
            "LD_LIBRARY_PATH": "/opt/click.ubuntu.com/.click/users/phablet/{0}/lib/{1}:/opt/click.ubuntu.com/.click/users/phablet/{0}/lib".format(package_name, self.config.arch_triplet),
            "PATH": "/opt/click.ubuntu.com/.click/users/phablet/{0}/lib/{1}/bin:/opt/click.ubuntu.com/.click/users/phablet/{0}:/home/phablet/bin:/home/phablet/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin".format(package_name, self.config.arch_triplet),
            "QML2_IMPORT_PATH": "/usr/lib/{0}/qt5/imports:/opt/click.ubuntu.com/.click/users/phablet/{1}/lib/{0}".format(self.config.arch_triplet, package_name),
            "UBUNTU_APP_LAUNCH_ARCH": self.config.arch_triplet,
            "APP_XMIR_ENABLE": "0",
            "DESKTOP_SESSION": "ubuntu-touch",
            "GDMSESSION": "ubuntu-touch",
            "GTK_IM_MODULE": "Maliit",
            "MIR_SERVER_HOST_SOCKET": "/run/mir_socket",
            "MIR_SERVER_NAME": "session-0",
            "MIR_SERVER_PROMPT_FILE": "1",
            "MIR_SOCKET": "/run/user/32011/mir_socket",
            "PULSE_CLIENTCONFIG": "/etc/pulse/touch-client.conf",
            "PULSE_PLAYBACK_CORK_STALLED": "1",
            "PULSE_PROP": "media.role=multimedia",
            "PULSE_SCRIPT": "/etc/pulse/touch.pa",
            "QML_NO_TOUCH_COMPRESSION": "1",
            "QT_ENABLE_GLYPH_CACHE_WORKAROUND": "1",
            "UBUNTU_APP_LAUNCH_XMIR_PATH": "/usr/bin/libertine-xmir",
            "UBUNTU_APPLICATION_ISOLATION": "1",
            "UPSTART_JOB": "application-click",
            "XDG_CACHE_HOME": "/home/phablet/.cache",
            "XDG_CONFIG_DIRS": "/etc/xdg/xdg-ubuntu-touch:/etc/xdg/xdg-ubuntu-touch:/etc/xdg",
            "XDG_CONFIG_HOME": "/home/phablet/.config",
            "XDG_CURRENT_DESKTOP": "Unity",
            "XDG_DATA_HOME": "/home/phablet/.local/share",
            "XDG_GREETER_DATA_DIR": "/var/lib/lightdm-data/phablet",
            "XDG_SEAT_PATH": "/org/freedesktop/DisplayManager/Seat0",
            "XDG_SEAT": "seat0",
            "XDG_SESSION_DESKTOP": "ubuntu-touch",
            "XDG_SESSION_PATH": "/org/freedesktop/DisplayManager/Session0",
            "XDG_SESSION_TYPE": "mir",
            "XDG_VTNR": "1",
        }

        return environ

    def get_cached_desktop_path(self):
        return os.path.join("/home/phablet/.cache/ubuntu-app-launch/desktop",
            "{}.desktop".format(self.get_app_id()))

    def kill_gdbserver(self):
        processes = self.device.run_command("ps aux | grep gdbserver",
                get_output=True)

        for line in processes.splitlines():
            if "gdbserver localhost:{}".format(self.port) in line:
                logger.debug("Killing running gdbserver on device")
                pid = line.split()[1]
                self.device.run_command("kill -9 {}".format(pid))

    def check_cached_desktop_file(self):
        path = self.get_cached_desktop_path()
        try:
            self.device.run_command("ls {} > /dev/null 2>&1".format(path),
                    get_output=True).strip()
        except:
            raise ClickableException('Failed to check installed version on device. The device is either not accessible or the app version you are trying to debug is not installed. Make sure the device is accessible or run "clickable install" and try again.')

    def push_gdbserver(self):
        self.config.container.pull_files(["/usr/bin/gdbserver"], "/tmp/clickable")
        self.device.push_file('/tmp/clickable/gdbserver', '/home/phablet/bin/gdbserver')

    def start_gdbserver(self):
        if not self.config.ssh:
            logger.warning('SSH is recommended for the "gdbserver" command. If you experience any issues, try again with "--ssh"')

        app_exec = self.get_app_exec_full_path()
        desktop_file = self.get_cached_desktop_path()
        app_dir = self.get_app_dir()
        environ = self.get_app_env()

        set_env = " ".join(["{}='{}'".format(key, value) for key, value in environ.items()])
        commands = [
                'cd {}'.format(app_dir),
                '{} gdbserver localhost:{} {} --desktop_file_hint={}'.format(
                    set_env, self.port, app_exec, desktop_file)
        ]

        self.set_signal_handler()
        self.device.run_command(commands, forward_port=self.port)

    def run(self, path_arg=None):
        self.port = 3333

        self.config.container.setup()
        self.check_cached_desktop_file()

        self.push_gdbserver()
        self.start_gdbserver()
